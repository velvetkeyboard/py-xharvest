# Core
import os
import time
import logging
import calendar
import threading
import urllib.parse
from operator import itemgetter
from datetime import date
from datetime import datetime
from datetime import timedelta
from decimal import getcontext
from decimal import Decimal
from configparser import ConfigParser

import keyring

# GTK
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository.WebKit2 import WebView
from gi.repository.WebKit2 import Settings

# Harvest API
from harvest.credentials import OAuth2Credential
from harvest.endpoints import OAuth2AccessTokenEndpoint
from harvest.endpoints import TimeEntryEndpoint
from harvest.endpoints import TimeEntryUpdateEndpoint
from harvest.endpoints import TimeEntryStopEndpoint
from harvest.endpoints import TimeEntryRestartEndpoint
from harvest.services import UsersAllAssignments
from harvest.services import TodayTimeEntries
from harvest.services import SingleDayTimeEntries
from harvest.services import MonthTimeEntries
from harvest.services import CurrentUser

# getcontext().prec = 3

LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG')

logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger('Harvest App')


class OAuth2CredentialManager(object):

    domain = 'https://id.getharvest.com'
    redirect_domain = 'http://localhost:8118'

    def get_credential(self):
        access_token = keyring.get_password("xharvest", "access_token")
        scope = keyring.get_password("xharvest", "scope")
        return OAuth2Credential(
                access_token,
                scope,
                )

    def set_access_token(self, access_token):
        keyring.set_password("xharvest", "access_token", access_token)

    def set_refresh_token(self, refresh_token):
        keyring.set_password("xharvest", "refresh_token", refresh_token)

    def set_expiration(self, expires_in):
        keyring.set_password("xharvest", "expires_in", expires_in)

    def set_last_request_date(self, date_str):
        keyring.set_password("xharvest", "last_request_date", date_str)

    def set_scope(self, scope):
        scope = urllib.parse.unquote(scope)
        scope = scope.split(':')[1].strip()
        keyring.set_password("xharvest", "scope", scope)

    def get_client_id(self):
        return keyring.get_password("xharvest", "client_id")

    def get_client_secret(self):
        return keyring.get_password("xharvest", "client_secret")

    def get_access_token(self):
        return keyring.get_password("xharvest", "access_token")

    def get_last_refresh_token(self):
        return keyring.get_password("xharvest", "refresh_token")

    def get_last_request_date(self):
        ret = keyring.get_password("xharvest", "last_request_date")
        if ret:
            ret = datetime.strptime(ret, "%Y-%m-%dT%H:%M:%S.%f")
        return ret

    def get_expiration_in_secs(self):
        return keyring.get_password("xharvest", "expires_in")

    def get_access_token_authorization_url(self):
        return '{}/oauth2/authorize?client_id={}&response_type=token'.format(
            self.domain,
            self.get_client_id())

    def is_access_token_expired(self):
        if keyring.get_password("xharvest", "access_token"):
            exp_in_sec = self.get_expiration_in_secs()
            last_request_date = self.get_last_request_date()
            if exp_in_sec and last_request_date:
                exp_delta = timedelta(seconds=int(exp_in_sec))
                expiration_date = last_request_date + exp_delta
                if datetime.now() < expiration_date:
                    return False

        return True


class Hour(object):

    HARVEST_MIN = Decimal(1) / Decimal(60)
    HARVEST_SEC = (Decimal(1) / Decimal(60)) / Decimal(60)

    def __init__(self, value):
        if '.' in str(value):
            value = ((Decimal(value) * 100) / self.HARVEST_SEC)/100
        elif ':' in str(value):
            hours, mins = value.split(':')
            value = (3600 * hours) + (60 * mins)
        # Total in secs
        self.value = int(value)

    def add_sec(self, increment=1):
        self.value += increment

    def add_min(self):
        self.value += 3600

    def as_harvest(self):
        return self.HARVEST_SEC * Decimal(self.value)

    def as_harvest_str(self):
        return f'{self.as_harvest():.2f}'

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value


class Task(object):
    def __init__(self, _id, name):
        self.id = _id
        self.name = name


class Project(object):
    def __init__(self, _id, name, tasks=None):
        self.id = _id
        self.name = name
        self.tasks = tasks or []

    def get_task_by_name(self, name):
        for task in self.tasks:
            if task.name == name:
                return task

class Task2(str):
    uid = None

class Project2(str):
    uid = None
    tasks = []

    def set_uid(self, uid):
        self.uid = uid


class TimeEntryWrapper(object):

    CHRONOMETER_DELAY = 37  # Seconds

    def __init__(self, time_entry, credential):
        self.time_entry = time_entry
        self.time_entry_id = time_entry['id']
        self.oauth2 = credential
        proj_name = self.time_entry['project']['name']
        task_name = self.time_entry['task']['name']
        builder = Gtk.Builder()
        builder.add_from_file("time_entry2.glade")
        builder.connect_signals(self)
        builder.get_object("gtkLabelTimeEntryTaskAndProjectName")\
                .set_markup(f"<b>{proj_name} - {task_name}</b>")
        builder.get_object("gtkTextViewTimeEntryNotes")\
                .set_markup(f"<i>{self.time_entry['notes']}</i>")

        self.pop_combobox_projects = builder.get_object('gtkComboBoxTextNewTimeEntryProject')
        self.pop_combobox_tasks = builder.get_object('gtkComboBoxTextNewTimeEntryTask')
        self.pop_textview_notes = builder.get_object('textViewTimeEntryNotes')
        self.pop_entry_hours = builder.get_object('entryTimeEntryHours')

        self.edit_button = builder.get_object("imageEditTimeEntry")
        self.contro_panel = builder.get_object("boxControlPanel")
        self.spinner = builder.get_object("spinnerTimeEntryUpdate")
        self.box = builder.get_object("gtkBoxTimeEntryWrapper")
        self.label = builder.get_object('gtkLabelTimeEntryHours')
        self.toggle_img = builder.get_object('imageTimeEntryToggleHours')
        self.update_hours_label(self.time_entry['hours'])
        self.hours = Hour(self.time_entry['hours'])
        self.source_remove_id = 0
        self.pop = builder.get_object('popoverTimeEntryForm')
        print(f'Is it running? - {self.time_entry["is_running"]}')
        if self.time_entry['is_running']:
            self.toggle_img.set_from_icon_name('gtk-media-pause', 1)
            self.spinner.show()
            self.spinner.start()
            self.source_remove_id = GLib.timeout_add_seconds(
                        self.CHRONOMETER_DELAY, self.chronometer)

    def render_combobox(self):
        self.assignments = UsersAllAssignments(credential=self.oauth2).all()

        for idx, assignment in enumerate(self.assignments):
            self.pop_combobox_projects.append(
                    str(assignment['project']['id']),
                    assignment['project']['name'],
                    )

            if assignment['project']['name'] == self.time_entry['project']['name']:
                self.pop_combobox_projects.set_active(idx)

                for idx2, task in enumerate(assignment['task_assignments']):
                    self.pop_combobox_tasks.append(
                            str(task['task']['id']),
                            task['task']['name'],
                            )

                    if task['task']['name'] == self.time_entry['task']['name']:
                        self.pop_combobox_tasks.set_active(idx2)

        self.pop_combobox_projects.connect('changed', self.combobox_projects_changed)

    def combobox_projects_changed(self, *args, **kwargs):
        project2 = self.pop_combobox_projects.get_active_text()
        self.pop_combobox_tasks.remove_all()
        for idx, task in enumerate(self.assignments['task_assignments']):
            self.pop_combobox_tasks.append(
                    str(task['task']['id']),
                    task['task']['name'],
                    )
            if task['task']['name'] == self.time_entry['task']['name']:
                self.pop_combobox_tasks.set_active(idx)

    def toggle_control_panel_visibility(self, *args, **kwargs):
        print('toggle_control_panel_visibility')
        self.render_combobox()
        self.pop_textview_notes.get_buffer().set_text(self.time_entry['notes'])
        self.pop_entry_hours.set_text(str(self.time_entry['hours']))
        self.pop.set_relative_to(self.edit_button)
        self.pop.set_position(Gtk.PositionType.BOTTOM)
        self.pop.show_all()
        self.pop.popup()
        #if self.contro_panel.is_visible():
        #    self.contro_panel.hide()
        #else:
        #    self.contro_panel.show()

    def update_hours_label(self, value):
        self.label.set_markup(f"<b>{value:.2f}</b>")

    def refresh_time_entry(self):
        resp = TimeEntryUpdateEndpoint(
            credential=self.oauth2,
            time_entry_id=self.time_entry['id']).get()
        if resp.status_code == 200:
            self.time_entry = resp.json()

    def chronometer(self):
        print('TimeEntryWrapper.chronometer - tick')
        self.hours.add_sec(self.CHRONOMETER_DELAY)
        print(self.hours.value)
        self.update_hours_label(self.hours.as_harvest())
        if self.source_remove_id:
            self.source_remove_id = GLib.timeout_add_seconds(
                self.CHRONOMETER_DELAY, self.chronometer)

    def toggle_chronometer(self, event_box, event_button):
        self.toggle_img.hide()
        self.refresh_time_entry()
        print(f'toggle_chronometer - running? - {self.time_entry["is_running"]}')
        if self.time_entry['is_running']:
            print(f'toggle_chronometer - stopping')
            resp = TimeEntryStopEndpoint(
                    self.oauth2, time_entry_id=self.time_entry['id']).patch()
            if resp.status_code == 200:
                self.time_entry = resp.json()
                self.update_hours_label(self.time_entry['hours'])
                self.spinner.stop()
                self.toggle_img.set_from_icon_name('gtk-media-play', 1)
            if self.source_remove_id:
                GLib.source_remove(self.source_remove_id)
                self.source_remove_id = 0

        else:
            print(f'toggle_chronometer - restarting')
            resp = TimeEntryRestartEndpoint(
                   self.oauth2, time_entry_id=self.time_entry['id']).patch()
            print(resp.status_code)
            if resp.status_code == 200:
                self.spinner.start()
                self.hours = Hour(self.time_entry['hours'])
                self.source_remove_id = GLib.timeout_add_seconds(
                        self.CHRONOMETER_DELAY, self.chronometer)
                self.toggle_img.set_from_icon_name('gtk-media-pause', 1)
                self.spinner.start()
        self.toggle_img.show()

    def update_time_entry(self, *args, **kwargs):
        print(args)
        notes_buffer = self.pop_textview_notes.get_buffer()
        notes = notes_buffer.get_text(
            notes_buffer.get_start_iter(),
            notes_buffer.get_end_iter(),
            True
            )
        hours = self.pop_entry_hours.get_text()
        project_id = self.pop_combobox_projects.get_active_id()
        task_id = self.pop_combobox_tasks.get_active_id()
        print(project_id)
        print(task_id)

    def delete_entry(self, event_box, event_button):
        print('delete_entry')

    def __str__(self):
        return f"{self.time_entry['id']} - {self.time_entry['hours']}"

    def __unicde__(self):
        return f"{self.time_entry['id']} - {self.time_entry['hours']}"

    def __repr__(self):
        return f"{self.time_entry['id']} - {self.time_entry['hours']}"


class App(object):

    def listbox_timeentry_remove(self, listbox, event_key):
        print(event_key.keyval)
        print(event_key.hardware_keycode)
        if event_key.keyval == 65535:  # Del Key
            eventbox_confirm = self.builder.get_object('eventBoxTimeEntryRemovalConfirm')
            eventbox_confirm.connect('button-press-event', self.remove_timeentry, listbox)
            self.builder.get_object('dialogTimeEntryRemoval').run()

    def remove_timeentry(self, event_box, event_button, listbox):
        self.main_spinner.start()
        self.main_spinner.show()
        event_box.get_parent().get_parent().get_parent().get_parent().hide()
        listboxrow = listbox.get_selected_row()
        print('listboxrow idx ', listboxrow.get_index())
        time_entry = self.selected_date_time_entries[listboxrow.get_index()]
        #for i in self.selected_date_time_entries:
        #    print (i['id'], i['notes'])
        #print('>>>', time_entry['notes'])
        listbox.remove(listboxrow)
        self.run_thread(
                self.remove_time_entry,
                [time_entry['id']],
                self.remove_time_entry_cb,
                [],
                )
        return True

    def time_entries_row_selected(self, listbox, listboxrow, *args, **kwargs):
        print('time_entries_row_selected')

    def time_entries_row_activated(self, listbox, listboxrow, *args, **kwargs):
        print('time_entries_row_activated now ', listboxrow.get_index())
        self.time_entry_listbox_clicks.append(
                datetime.now()
                )
        print('time_entries_row_activated last click ', self.time_entry_listbox_clicks)
        if len(self.time_entry_listbox_clicks) == 2:
            time_elapsed = self.time_entry_listbox_clicks[1] - \
                           self.time_entry_listbox_clicks[0]
            if time_elapsed.seconds <= 2:
                print('open dialog for editting')
            self.time_entry_listbox_clicks = []

        return True

    def __init__(self):
        self.builder = Gtk.Builder()
        self.oauth2 = OAuth2CredentialManager()
        self.time_entry_wrappers = []
        self.last_time_entry_selected = None
        self.time_entry_listbox_clicks = []

    def run_thread(self, async_fn, async_fn_args, async_cb, async_cb_args):
        thread = threading.Thread(target=async_fn, args=async_fn_args)
        thread.daemon = True
        thread.start()
        GLib.idle_add(async_cb, *([thread] + async_cb_args))

    def start(self):
        self.builder.add_from_file("main.glade")
        self.builder.connect_signals(self)
        self.main_window = self.builder.get_object("main_window")

        if self.oauth2.is_access_token_expired():
            self.show_authentication_window()
        else:
            self.show_main_window()
        Gtk.main()

    # ---( API Calls )--------------------------------------------------------

    def fetch_current_user(self):
        self.user = CurrentUser(self.oauth2.get_credential()).get()

    def fetch_initial_data(self):
        self.fetch_current_user()
        self.fetch_timeentries_from_selected_date()

    def fetch_user_assignments(self):
        self.assignments = UsersAllAssignments(
                credential=self.oauth2.get_credential()).all()

    def fetch_timeentries_from_selected_date(self):
        svc = SingleDayTimeEntries(
            self.oauth2.get_credential(),
            self.selected_date.isoformat(),
            )
        resp = svc.all()
        self.selected_date_time_entries = resp['time_entries']

    def remove_time_entry(self, time_entry_id):
        resp = TimeEntryUpdateEndpoint(
                    self.oauth2.get_credential(),
                    time_entry_id=time_entry_id,
                    ).delete()
        self.fetch_timeentries_from_selected_date()

    # ---( Fetch Data Callbacks )----------------------------------------------

    def fetch_initial_data_cb(self, thread, *args, **kwargs):
        if thread.is_alive():
            return True

        thread.join()
        self.render_time_entries()
        self.main_spinner.stop()
        self.main_spinner.hide()

    def fetch_user_assignments_cb(self, thread, *args, **kwargs):
        if thread.is_alive():
            return True

        thread.join()
        self.render_assignments()
        self.main_spinner.stop()
        self.main_spinner.hide()

    def remove_time_entry_cb(self, thread, *args, **kwargs):
        if thread.is_alive():
            return True

        thread.join()
        self.render_time_entries()
        self.main_spinner.stop()
        self.main_spinner.hide()

    # ---( Initial Flows )-----------------------------------------------------

    def webview_navigate(self, web_view, decision, decision_type):
        # def get_param(webview, val):
        #     return {
        #         e.split('=')[0]: e.split('=')[1]
        #         for e in web_view.get_uri().split('?')[1].split('&')
        #     }[val]

        uri = web_view.get_uri()
        if (uri.startswith(self.oauth2.redirect_domain)):
            decision.ignore()
            params = uri.split('?')[1].split('&')
            params = {txt.split('=')[0]: txt.split('=')[1] for txt in params}
            # Storing Credentials
            self.oauth2.set_access_token(params['access_token'])
            self.oauth2.set_expiration(params['expires_in'])
            self.oauth2.set_last_request_date(datetime.now().isoformat())
            self.oauth2.set_scope(params['scope'])
            self.win_oauth2_signin.destroy()
            # Running Regular Flow
            self.show_main_window()
            return True
        return False

    def show_authentication_window(self):
        self.win_oauth2_signin = self.builder.get_object("windowHarvestOAuth2Authorization")
        self.win_oauth2_signin.show_all()
        webview = self.builder.get_object("webkitwebviewOAuth2Authorization")
        webview.load_uri(self.oauth2.get_access_token_authorization_url())
        webview.connect("decide-policy", self.webview_navigate)

    def show_main_window(self):
        self.selected_date = date.today()
        self.main_spinner = self.builder.get_object('spinnerTimeEntryList')
        self.main_spinner.start()
        self.main_spinner.show()

        # Pulling Time Entries for Today
        self.run_thread(self.fetch_initial_data, [],
                        self.fetch_initial_data_cb, [])

        self.render_weekdays()
        self.builder.get_object("gtkLabelWeekNumber")\
                .set_label(f"{self.get_week_number()}/54")
        self.main_window.show_all()

    # ---( Common Renderings )-------------------------------------------------

    def render_month_hours(self):
        svc = MonthTimeEntries(self.oauth2)
        svc.set_month(self.selected_date.year, self.selected_date.month)
        time_entries = svc.all()

    def render_time_entries(self):
        children = self.get_timeentry_list().get_children()#.remove_all()
        for child in children:
            self.get_timeentry_list().remove(child)
        day_hours = Decimal(0.0)
        self.selected_date_time_entries.sort(
            key=itemgetter('created_at'))
        self.time_entry_wrappers = []
        self.last_time_entry_selected = None
        for entry in self.selected_date_time_entries:
            print(entry['created_at'])
            day_hours += Decimal(entry['hours'])
            te = TimeEntryWrapper(entry, self.oauth2.get_credential())
            self.time_entry_wrappers.append(te)
            self.get_timeentry_list().add(te.box)
        self.builder.get_object('labelTodayHours')\
            .set_label(f'{day_hours:.2f}')

    def render_weekdays(self):
        self.selected_week_dates = []
        week_day_labels = [
            self.builder.get_object("labelMonday"),
            self.builder.get_object("labelTuesday"),
            self.builder.get_object("labelWednesday"),
            self.builder.get_object("labelThursday"),
            self.builder.get_object("labelFriday"),
            self.builder.get_object("labelSaturday"),
            self.builder.get_object("labelSunday"),
        ]
        start = 0 - self.selected_date.weekday()
        end = 7 - self.selected_date.weekday()
        for i in range(start, end):
            wdate = self.selected_date + timedelta(days=i)
            self.selected_week_dates.append(wdate)
            wdate_name = calendar.day_name[wdate.weekday()][:3]
            print(wdate_name, wdate, wdate.weekday())
            label = f'{wdate_name}\n{wdate.day:02d}/{wdate.month:02d}'
            if self.selected_date.weekday() == wdate.weekday():
                week_day_labels[wdate.weekday()].set_markup(f'<b>{label}</b>')
            else:
                week_day_labels[wdate.weekday()].set_label(f'{label}')

    def render_assignments(self):
        self.project_assignments = {}
        newtimeentry_dialog = self.builder.get_object("gtkDialogNewTimeEntry")
        combobox_projects = self.builder.get_object("gtkComboBoxTextNewTimeEntryProject")

        for assignment in self.assignments:
            tasks = []
            for task in assignment['task_assignments']:
                tasks.append(Task(
                    task['task']['id'],
                    task['task']['name'],
                ))
            p = Project(
                _id=assignment['project']['id'],
                name=assignment['project']['name'],
                tasks=tasks,
            )
            self.project_assignments[assignment['project']['name']] = p
            combobox_projects.append_text(assignment['project']['name'])

        #newtimeentry_dialog.run()

        popover = self.builder.get_object("popoverTimeEntryForm")
        popover.set_relative_to(self.builder.get_object("eventBoxNewTimeEntry"))
        popover.show_all()
        popover.popup()

    # ---( Time Entries Management )-------------------------------------------

    def create_new_entry(self, button):
        self.main_spinner.start()
        self.main_spinner.show()
        popover = self.builder.get_object("popoverTimeEntryForm")
        popover.popdown()
        project_name = self.builder.get_object("gtkComboBoxTextNewTimeEntryProject").get_active_text()
        task_name = self.builder.get_object("gtkComboBoxTextNewTimeEntryTask").get_active_text()
        notes_buffer = self.builder.get_object("gtkComboBoxTextNewTimeEntryNotes").get_buffer()
        hours = self.builder.get_object('entryTimeEntryHours').get_text()
        notes = notes_buffer.get_text(
            notes_buffer.get_start_iter(),
            notes_buffer.get_end_iter(),
            True
            )
        spent_date = self.selected_date.isoformat()
        project = self.project_assignments[project_name]
        project_id = project.id
        task_id = project.get_task_by_name(task_name).id
        data = {
            'user_id': self.user['id'],
            'notes': notes,
            'spent_date': spent_date,
            'task_id': task_id,
            'project_id': project_id,
            'hours': hours,
        }
        resp = TimeEntryEndpoint(
            credential=self.oauth2.get_credential()).post(data=data)
        if resp.status_code == 201:
            tew = TimeEntryWrapper(
                    time_entry=resp.json(),
                    credential=self.oauth2.get_credential(),
                    )
            self.get_timeentry_list().add(tew.box)
            #self.hide_new_timeentry_dialog(button)
            self.main_spinner.stop()
            self.main_spinner.hide()

    def show_new_timeentry_dialog(self, event_box, event_button):
        self.main_spinner.start()
        self.main_spinner.show()
        self.run_thread(self.fetch_user_assignments, [],
                        self.fetch_user_assignments_cb, [])

    def hide_new_timeentry_dialog(self, button):
        self.project_assignments = {}
        self.builder.get_object("gtkComboBoxTextNewTimeEntryProject").remove_all()
        self.builder.get_object("gtkComboBoxTextNewTimeEntryTask").remove_all()
        self.builder.get_object("gtkComboBoxTextNewTimeEntryNotes").get_buffer().set_text('')
        self.builder.get_object("gtkDialogNewTimeEntry").hide()
        # self.builder.get_object("gtkDialogNewTimeEntry").emit("close")

    def combobox_projects_on_change(self, combobox_text):
        if self.project_assignments:
            text = combobox_text.get_active_text()
            combobox_tasks = self.builder.get_object("gtkComboBoxTextNewTimeEntryTask")
            combobox_tasks.remove_all()
            for task in self.project_assignments[text].tasks:
                combobox_tasks.append_text(task.name)

    def get_timeentry_list(self):
        return self.builder.get_object("gtkListBoxTimeEntries")

    # --(Events)--------------------------------------------

    def get_week_number(self):
        return self.selected_date.isocalendar()[1]

    def get_timeentries(self, event_box, event_button):
        self.selected_date = self.selected_week_dates[int(event_box.get_name())]
        self.render_weekdays()
        self.wipe_time_entries()
        self.main_spinner.start()
        self.main_spinner.show()
        self.run_thread(self.fetch_timeentries_from_selected_date, [],
                        self.fetch_initial_data_cb, [])

    def get_today_time_entries(self, event_box, event_button):
        self.selected_date = date.today()
        self.render_weekdays()
        self.wipe_time_entries()
        self.main_spinner.start()
        self.main_spinner.show()
        self.run_thread(self.fetch_timeentries_from_selected_date, [],
                        self.fetch_initial_data_cb, [])

    def get_last_week_timeentries(self, event_box, event_button):
        self.selected_date = self.selected_date - timedelta(
            days=self.selected_date.weekday() + 1)
        self.render_weekdays()
        self.wipe_time_entries()
        self.main_spinner.start()
        self.main_spinner.show()
        self.run_thread(self.fetch_timeentries_from_selected_date, [],
                        self.fetch_initial_data_cb, [])

    def get_next_week_timeentries(self, event_box, event_button):
        self.selected_date = self.selected_date + timedelta(
            days=7 - self.selected_date.weekday())
        self.render_weekdays()
        self.wipe_time_entries()
        self.main_spinner.start()
        self.main_spinner.show()
        self.run_thread(self.fetch_timeentries_from_selected_date, [],
                        self.fetch_initial_data_cb, [])

    # ---( Utilities )---------------------------------------------------------

    def wipe_time_entries(self):
        children = self.get_timeentry_list().get_children()
        for child in children:
            self.get_timeentry_list().remove(child)

    def get_month_hours(self):
        svc = MonthTimeEntries()
        svc.set_month(
            self.selected_date.year, self.selected_date.month)
        resp = svc.all()
        month_hours = Decimal(0)
        for entry in resp['time_entries']:
            month_hours += Decimal(entry['hours'])
        self.builder.get_object("gtkLabelMonthHours").set_label(str(month_hours))

    def quit(self, *args):
        Gtk.main_quit()


if __name__ == '__main__':
    app = App()
    app.start()
