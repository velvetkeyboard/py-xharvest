# Core
import os
import time
import logging
import calendar
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
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf 
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject
from gi.repository.WebKit2 import WebView
from gi.repository.WebKit2 import Settings

# Harvest API
from harvest.credentials import *
from harvest.endpoints import *
from harvest.services import *

# Src
from xharvest.logs import logger
from xharvest.data_structures import *
from xharvest.gtk_traits import *
from xharvest.threads import *
from xharvest.data_structures import *

# Traits
# -----------------------------------------------------------------------------

Gtk.Widget.find_child_by_name = trait_find_child_by_name
Gtk.ListBox.remove_all = trait_remove_all
Gtk.Box.remove_all = trait_remove_all

# Managers
# -----------------------------------------------------------------------------

class WeekTimeEntriesService(TimeRangeBaseService):
    def __init__(self, credential, date):
        '''
        Params:
            data (datetime.datetime):
        '''
        self.date = date
        super(WeekTimeEntriesService, self).__init__(credential)

    def get_date_range(self):
        start = self.date + timedelta(0 - self.date.weekday())
        end = self.date + timedelta(6 - self.date.weekday())
        print('WeekTimeEntriesService', start, end)
        ret = (
            start.date(),
            end.date(),
        )
        return ret


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

    def set_scope(self, scope):
        scope = urllib.parse.unquote(scope)
        scope = scope.split(':')[1].strip()
        keyring.set_password("xharvest", "scope", scope)

    def set_refresh_token(self, refresh_token):
        keyring.set_password("xharvest", "refresh_token", refresh_token)

    def set_expiration(self, expires_in):
        keyring.set_password("xharvest", "expires_in", expires_in)

    def set_last_request_date(self, date_str):
        keyring.set_password("xharvest", "last_request_date", date_str)

    def get_client_id(self):
        return keyring.get_password("xharvest", "client_id")

    def get_client_secret(self):
        return keyring.get_password("xharvest", "client_secret")

    def get_access_token(self):
        return keyring.get_password("xharvest", "access_token")

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


class TimeEntryListBoxRow(Gtk.ListBoxRow):
    CHRONOMETER_DELAY = 37  # Seconds
    # CHRONOMETER_DELAY = 2

    def __init__(self, data, app_start_time_entry_cb, app_stop_time_entry_cb):
        super(Gtk.ListBoxRow, self).__init__()
        # self.obj = obj
        self.data = data
        self.source_remove_id = None
        self.app_start_time_entry_cb = app_start_time_entry_cb
        self.app_stop_time_entry_cb = app_stop_time_entry_cb
        builder = Gtk.Builder()
        # builder.add_from_file('main2.glade')
        builder.add_objects_from_file('main2.glade', ('boxTimeEntry',))
        self.bind(builder)
        box = builder.get_object('boxTimeEntry')
        self.add(box)
        if self.data['is_running']:
            self.start_chronometer()
            self.render_start_chronometer()

    def bind(self, builder):
        # print(self.data)
        builder.get_object('labelTimeEntryNotes').set_markup(
            f"<i>{self.data['notes']}</i>")
        builder.get_object('labelTimeEntryProject').set_markup(
            "<b>[{}] {}</b>".format(
                self.data['project']['code'],
                self.data['project']['name'],
                ))
        builder.get_object('labelTimeEntryTask').set_markup(
            f"<b>{self.data['task']['name']}</b>")
        self.spn_hours = builder.get_object('spinnerTimeEntry')
        self.toggle_img = builder.get_object('imageTimeEntryToggleRunning')
        builder.get_object('eventBoxTimeEntryToggleRunning')\
            .connect('button-press-event', self.toggle_chronometer)
        self.lbl_hours = builder.get_object('labelTimeEntryHours')
        self.lbl_hours.set_markup(f"<b>{self.data['hours']}</b>")

    def update_hours_label(self, val):
        self.lbl_hours.set_markup(
            f"<b>{val:.2f}</b>")

    def chronometer(self):
        self.hours.add_sec(self.CHRONOMETER_DELAY)
        print('TimeEntryListBoxRow', self.data['id'], 'chronometer', 'tick', self.hours.value)
        print('TimeEntryListBoxRow', self.data['id'], 'chronometer', 'cb id', self.source_remove_id)
        self.update_hours_label(self.hours.as_harvest())
        if self.source_remove_id:
            GLib.source_remove(self.source_remove_id)
        if self.data['is_running']:
            self.source_remove_id = GLib.timeout_add_seconds(
                            self.CHRONOMETER_DELAY,
                            self.chronometer,
                            )

    def toggle_chronometer(self, event_box=None, event_button=None):
        # self.toggle_img.hide()
        # self.refresh_time_entry()
        print('TimeEntryListBoxRow', 'toggle_chronometer', self.data['id'], 'is_running', self.data['is_running'])
        if self.data['is_running']:
            self.stop_chronometer()
        else:
            self.start_chronometer()

    def start_chronometer(self):
        print('TimeEntryListBoxRow', 'start_chronometer', self.data['id'])
        self.app_start_time_entry_cb(self, self.data['id'])

    def stop_chronometer(self):
        print('TimeEntryListBoxRow', 'stop_chronometer', self.data['id'])
        if self.source_remove_id:
            GLib.source_remove(self.source_remove_id)
            self.source_remove_id = None
        self.hours = Hour(self.data['hours'])
        self.app_stop_time_entry_cb(self, self.data['id'])

    def render_start_chronometer(self):
        print('TimeEntryListBoxRow', 'render_start_chronometer', self.data['id'])
        self.hours = Hour(self.data['hours'])
        self.source_remove_id = GLib.timeout_add_seconds(
                        self.CHRONOMETER_DELAY,
                        self.chronometer,
                        )
        self.toggle_img.set_from_icon_name('gtk-media-pause', 1)
        self.spn_hours.start()

    def render_stop_chronometer(self):
        print('TimeEntryListBoxRow', 'render_stop_chronometer', self.data['id'])
        self.toggle_img.set_from_icon_name('gtk-media-play', 1)
        self.spn_hours.stop()


class WeekDayBox(Gtk.Box):

    def set_bold(self):
        w = self.find_child_by_name('labelWeekDayName')
        w.set_markup(f"<b>{w.get_label()}</b>")
        w = self.find_child_by_name('labelWeekDayDate')
        w.set_markup(f"<b>{w.get_label()}</b>")

    def set_normal(self):
        w = self.find_child_by_name('labelWeekDayName')
        txt = w.get_label().replace('<b>', '').replace('</b>', '')
        w.set_label(f"{txt}")
        w = self.find_child_by_name('labelWeekDayDate')
        txt = w.get_label().replace('<b>', '').replace('</b>', '')
        w.set_label(f"{txt}")


class AppHandler(object):

    NEXT_WEEK = 1
    PREV_WEEK = 2

    # Auth --------------------------------------------------------------------

    def webview_navigate(self, web_view, decision, decision_type):
        uri = web_view.get_uri()
        if (uri.startswith(self.oauth2_mng.redirect_domain)):
            decision.ignore()
            params = uri.split('?')[1].split('&')
            params = {txt.split('=')[0]: txt.split('=')[1] for txt in params}
            # Storing Credentials
            self.oauth2_mng.set_access_token(params['access_token'])
            self.oauth2_mng.set_expiration(params['expires_in'])
            self.oauth2_mng.set_last_request_date(datetime.now().isoformat())
            self.oauth2_mng.set_scope(params['scope'])
            self.win_oauth2_signin.destroy()

            # Running Regular Flow
            self.win.show_all()
            self.spn_timeentries.show()
            self.spn_timeentries.start()

            CustomThread(
                target=self.initial_api_calls_async,
                target_cb=self.initial_api_calls_cb,
            ).start()

            return True
        return False

    def __init__(self, builder):
        self.oauth2_mng = OAuth2CredentialManager()
        self.assignments = []
        self.user = None
        self.last_refresh_assignments = None
        self.selected_date = datetime.now()
        self.time_entries = []
        self.listorwbox_time_entry_running = None
        self.time_entry_running = None

        # Core Widgets --------------------------------------------------------
        self.builder = builder
        self.win = self.builder.get_object('window')
        self.lbox_timeentries = self.builder.get_object('listBoxTimeEntries')
        self.box_weekdays = self.builder.get_object('boxWeekDays')
        self.spn_timeentries = self.builder.get_object('spinnerTimeEntries')
        self.pop_time_entry = self.builder.get_object('popoverNewTimeEntry')
        self.ebx_time_entry = self.builder.get_object('eventBoxCreateNewTimeEntry')

        self.ebx_time_entry.connect(
            'button-press-event', self.open_time_entry_form)

        # Pulling Initial API Data
        if not self.oauth2_mng.is_access_token_expired():
            self.spn_timeentries.show()
            self.spn_timeentries.start()
            self.win.show_all()
            CustomThread(
                target=self.initial_api_calls_async,
                target_cb=self.initial_api_calls_cb,
            ).start()

        else:
            self.render_authentication_window()

    # Api Wrappers ------------------------------------------------------------

    def refresh_current_user(self):
        self.user = CurrentUser(self.oauth2_mng.get_credential()).get()

    def refresh_assignments(self):
        self.assignments = UsersAllAssignments(
            credential=self.oauth2_mng.get_credential()).all()
        self.last_refresh_assignments = datetime.now()

    def refresh_time_entries(self):
        self.time_entries = WeekTimeEntriesService(
            self.oauth2_mng.get_credential(),
            self.selected_date,
            ).all()['time_entries']

    # Async / Callbacks -------------------------------------------------------

    def initial_api_calls_async(self):
        self.refresh_current_user()
        self.refresh_assignments()
        self.refresh_time_entries()

    @gtk_thread_class_cb
    def initial_api_calls_cb(self, thread):
        self.render_weekdays()
        self.render_time_entries()
        # self.render_about_user()
        self.spn_timeentries.hide()
        self.spn_timeentries.stop()

    def shift_week_async(self):
        self.refresh_time_entries()

    @gtk_thread_class_cb
    def shift_week_cb(self, thread):
        self.render_time_entries()
        self.spn_timeentries.hide()
        self.spn_timeentries.stop()

    # Rendering ---------------------------------------------------------------

    def render_about_user(self):
        self.builder.get_object('labelAuthUserFullName')\
            .set_label(f"{self.user['first_name']} {self.user['last_name']}")
        self.builder.get_object('labelAuthUserEmail')\
            .set_label(self.user['email'])
        self.builder.get_object('imageAuthUserAvatar')\
                    .set_from_pixbuf(self.get_user_avatar_img_as_pixbuf())

    def render_authentication_window(self):
        builder = Gtk.Builder()
        builder.add_objects_from_file('main2.glade', ('windowHarvestOAuth2Authorization',))
        self.win_oauth2_signin = builder.get_object('windowHarvestOAuth2Authorization')
        self.win_oauth2_signin.show_all()
        webview = builder.get_object("webkitwebviewOAuth2Authorization")
        webview.load_uri(self.oauth2_mng.get_access_token_authorization_url())
        webview.connect("decide-policy", self.webview_navigate)

    def render_weekday_widget(self, data):
        builder = Gtk.Builder()
        builder.add_objects_from_file('main2.glade', ('eventBoxWeekDay',))

        if data['selected_date']:
            builder.get_object('labelWeekDayName').set_markup(
                f"<b>{data['week_day_name']}</b>")
            builder.get_object('labelWeekDayDate').set_markup(
                f"<b>{data['week_day_date']}</b>")
        else:
            builder.get_object('labelWeekDayName').set_markup(
                f"{data['week_day_name']}")
            builder.get_object('labelWeekDayDate').set_markup(
                f"{data['week_day_date']}")

        builder.get_object('eventBoxWeekDay').set_name(
                data['week_day_data_iso'])

        root_widget = builder.get_object('eventBoxWeekDay')
        root_widget.connect('button-press-event', self.select_weekday)
        ret = WeekDayBox()
        ret.add(root_widget)
        ret.data = data
        return ret

    def render_weekdays(self):
        start = 0 - self.selected_date.date().weekday()
        end = 7 - self.selected_date.date().weekday()
        self.box_weekdays.remove_all()
        for i in range(start, end):
            wdate = self.selected_date + timedelta(days=i)
            wdate_name = calendar.day_name[wdate.weekday()][:3]
            data = {
                'week_day_date': f'{wdate.day:02d}/{wdate.month:02d}',
                'week_day_name': wdate_name,
                'selected_date': self.selected_date == wdate,
                'week_day_data_iso': wdate.isoformat(),
            }
            widget = self.render_weekday_widget(data)
            self.box_weekdays.add(widget)
        self.box_weekdays.show_all()

    def render_time_entries(self):
        self.lbox_timeentries.remove_all()
        self.time_entries.sort(
            key=itemgetter('spent_date'))
        for entry in self.time_entries:
            print('time_entry', entry['id'], entry['notes'][:30])
            if entry['is_running']:
                self.time_entry_running = entry['id']
            if self.selected_date.date() == \
                datetime.strptime(entry['spent_date'], '%Y-%m-%d').date():
                lboxrow = TimeEntryListBoxRow(
                    entry,
                    self.timeentrylistrow_start_time_entry,
                    self.timeentrylistrow_stop_time_entry,
                    )
                evbox = lboxrow.find_child_by_name('eventBoxTimeEntryEdit')
                evbox.connect(
                    'button-press-event',
                    self.render_popover_time_entry_for_update,
                    lboxrow,
                    )
                self.lbox_timeentries.add(lboxrow)

        self.lbox_timeentries.show_all()

    def render_popover_time_entry_for_creation(self):
        cbx_proj = self.builder.get_object('comboBoxTextNewTimeEntryProject')
        cbx_task = self.builder.get_object('comboBoxTextNewTimeEntryTask')

        for a in self.assignments:
            cbx_proj.append(str(a['project']['id']), a['project']['name'])
        cbx_proj.connect('changed', self.combobox_projects_changed)

        self.builder.get_object('comboBoxTextNewTimeEntryProject').set_active(-1)
        self.builder.get_object('comboBoxTextNewTimeEntryTask').set_active(-1)
        self.builder.get_object('textViewNewTimeEntryNotes').get_buffer().set_text('')
        self.builder.get_object('entryNewTimeEntryHours').set_text('')

        self.builder.get_object('buttonCreateOrUpateNewTimeEntry')\
            .connect('clicked', self.create_or_update_time_entry)
        self.builder.get_object('eventBoxDeleteTimeEntry').hide()

        self.pop_time_entry.set_relative_to(self.ebx_time_entry)
        self.pop_time_entry.popup()

    def render_popover_time_entry_for_update(self, event_box=None, event_button=None, lboxrow=None):
        cbx_proj = self.builder.get_object('comboBoxTextNewTimeEntryProject')
        cbx_task = self.builder.get_object('comboBoxTextNewTimeEntryTask')

        for a in self.assignments:
            cbx_proj.append(f"{a['project']['id']}", a['project']['name'])
            if str(lboxrow.data['project']['id']) == str(a['project']['id']):
                for t in a['task_assignments']:
                    cbx_task.append(f"{t['task']['id']}", t['task']['name'])

        cbx_proj.set_active_id(str(lboxrow.data['project']['id']))
        cbx_task.set_active_id(str(lboxrow.data['task']['id']))

        cbx_proj.connect('changed', self.combobox_projects_changed, lboxrow.data)

        self.builder.get_object('textViewNewTimeEntryNotes')\
            .get_buffer().set_text(lboxrow.data['notes'])
        self.builder.get_object('entryNewTimeEntryHours')\
            .set_text(f"{lboxrow.data['hours']}")

        self.builder.get_object('buttonCreateOrUpateNewTimeEntry')\
            .connect('clicked', self.create_or_update_time_entry, lboxrow.data['id'])

        self.builder.get_object('eventBoxDeleteTimeEntry')\
            .connect('button-press-event', self.delete_time_entry, lboxrow.data['id'])

        self.builder.get_object('eventBoxDeleteTimeEntry').show()

        self.pop_time_entry.set_relative_to(event_box)
        self.pop_time_entry.popup()

    # Event -------------------------------------------------------------------

    def get_last_week_timeentries(self, event_box, event_button):
        self.shift_week(self.PREV_WEEK)

    def get_next_week_timeentries(self, event_box, event_button):
        self.shift_week(self.NEXT_WEEK)

    def open_time_entry_form(self, event_box, event_button):
        self.render_popover_time_entry_for_creation()

    def combobox_projects_changed(self, cbx, data=None):
        proj_id = cbx.get_active_id()
        print('proj_id =', proj_id)
        cbx_task = self.builder.get_object('comboBoxTextNewTimeEntryTask')
        cbx_task.remove_all()
        for p in self.assignments:
            print('project id =', p['project']['id'])
            if str(p['project']['id']) == str(proj_id):
                for t in p['task_assignments']:
                    print('processing task >>>', t)
                    cbx_task.append(f"{t['task']['id']}", t['task']['name'])
                break

        if data:
            cbx_task.set_active_id(str(data['task']['id']))

    def create_or_update_time_entry(self, button, time_entry_id=None):
        btn = self.builder.get_object('buttonCreateOrUpateNewTimeEntry')
        btn.hide()
        spn = self.builder.get_object('spinnerCreatingNewTimeEntry')
        spn.start()
        spn.show()

        cbx_proj = self.builder.get_object('comboBoxTextNewTimeEntryProject')
        cbx_task = self.builder.get_object('comboBoxTextNewTimeEntryTask')
        txt_notes = self.builder.get_object('textViewNewTimeEntryNotes')
        ent_hours = self.builder.get_object('entryNewTimeEntryHours')

        project_id = cbx_proj.get_active_id().split('@')[0]
        task_id = cbx_task.get_active_id()
        bf = txt_notes.get_buffer()
        notes = bf.get_text(bf.get_start_iter(), bf.get_end_iter(), True)
        spent_date = datetime.now().date().isoformat()
        hours = ent_hours.get_text()

        data = {
            'user_id':self.user['id'],
            'notes': notes,
            'spent_date': spent_date,
            'task_id': int(task_id),
            'project_id': int(project_id),
            'hours': hours,
        }

        api_resp = {'requests': {}}

        @gtk_thread_cb
        def cb(thread, resp):
            spn.hide()
            spn.stop()
            btn.show()

            if resp['requests']['response'].status_code == 201 or \
                resp['requests']['response'].status_code == 200:
                cbx_proj.set_active(-1)
                cbx_task.set_active(-1)
                bf.set_text('')
                ent_hours.set_text('')
                time_entry = resp['requests']['response'].json()

                print('time entry -> spent_date', time_entry['spent_date'])
                print('time entry -> created_at', time_entry['created_at'])
                print('time entry -> updated_at', time_entry['updated_at'])

                if time_entry['created_at'] == time_entry['updated_at']:
                    self.time_entries.append(time_entry)
                else:
                    idx = -1
                    for entry in self.time_entries:
                        if entry['id'] == time_entry['id']:
                            idx = self.time_entries.index(entry)
                    self.time_entries[idx] = dict(time_entry)

                self.pop_time_entry.popdown()
                self.render_time_entries()

            else:
                btn.set_label('Try Again')

        if time_entry_id:  # Updating
            def t1(data, resp):
                print('Updating Time Entry')
                resp['requests']['response'] = TimeEntryUpdateEndpoint(
                    credential=self.oauth2_mng.get_credential(),
                    time_entry_id=time_entry_id,
                    ).patch(data=data)
            CustomThread(
                target=t1,
                args=(data, api_resp),
                target_cb=cb,
                target_cb_args=[api_resp,],
                ).start()

        else:  # Creating
            print('Creating Time Entry')
            def t2(data, resp):
                resp['requests']['response'] = TimeEntryEndpoint(
                    credential=self.oauth2_mng.get_credential()).post(data=data)

            CustomThread(
                target=t2,
                args=(data, api_resp),
                target_cb=cb,
                target_cb_args=[api_resp,],
                ).start()

    def delete_time_entry(self, event_box, event_button, time_entry_id):
        btn = self.builder.get_object('buttonCreateOrUpateNewTimeEntry')
        btn.hide()
        ebx_delete = self.builder.get_object('eventBoxDeleteTimeEntry')
        ebx_delete.hide()
        spn = self.builder.get_object('spinnerCreatingNewTimeEntry')
        spn.start()
        spn.show()
        api_resp = {'requests': {}}
        x = 'x'

        def t(resp):
            print('Deleting Time Entry', time_entry_id)
            print('Thread - Resp', type(resp))
            resp['requests']['response'] = TimeEntryUpdateEndpoint(
                credential=self.oauth2_mng.get_credential(),
                time_entry_id=time_entry_id,
                ).delete()

        @gtk_thread_cb
        def cb(thread, resp):
            spn.hide()
            spn.stop()
            btn.show()
            ebx_delete.show()
            if resp['requests']['response'].status_code == 201 or \
                resp['requests']['response'].status_code == 200:
                # time_entry = resp['requests']['response'].json()
                print('Removing time_entry')
                idx = -1
                for entry in self.time_entries:
                    if entry['id'] == time_entry_id:
                        idx = self.time_entries.index(entry)
                        break

                del self.time_entries[idx]

                self.pop_time_entry.popdown()
                self.render_time_entries()

            else:
                btn.set_label('Try Again')

        CustomThread(
            target=t,
            args=(api_resp,),
            target_cb=cb,
            target_cb_args=[api_resp,],
            ).start()

    def show_settings_menu(self, event_box, event_button):
        # self.builder.get_object('popoverSettings').popup()
        # self.builder.get_object('appWindowSettings').show_all()
        # ('appWindowSettings')
        pass

    def timeentrylistrow_start_time_entry(self, listrowbox, time_entry_id):
        print('app', 'timeentrylistrow_start_time_entry', 'trying to start time entry', time_entry_id)
        if self.time_entry_running and self.time_entry_running != time_entry_id:
            print('app', 'timeentrylistrow_start_time_entry', 'running time entry', self.time_entry_running)
            # Updating UI
            updated_at_ui = False
            for listboxrow2 in self.lbox_timeentries:
                if listboxrow2.data['id'] == self.time_entry_running:
                    listboxrow2.stop_chronometer()
                    updated_at_ui = True
                    break
            if not updated_at_ui:
                # Updating API data
                resp = TimeEntryStopEndpoint(
                    self.oauth2_mng.get_credential(),
                    time_entry_id=self.time_entry_running
                    ).patch()
                print('app', 'timeentrylistrow_start_time_entry', 'updated', resp.status_code)
                # Updating Local data
                idx = -1
                for i, time_entry in enumerate(self.time_entries):
                    if time_entry['id'] == resp.json()['id']:
                        idx = i
                print('app', 'timeentrylistrow_start_time_entry', 'local time entry', self.time_entries[idx]['is_running'])
                self.time_entries[idx] = resp.json()
                print('app', 'timeentrylistrow_start_time_entry', 'local time entry', self.time_entries[idx]['is_running'])


        resp = TimeEntryRestartEndpoint(
            self.oauth2_mng.get_credential(),
            time_entry_id=time_entry_id
            ).patch()
        if resp.status_code == 200:
            self.time_entry_running = time_entry_id
            listrowbox.render_start_chronometer()

    def timeentrylistrow_stop_time_entry(self, listrowbox, time_entry_id):
        print('app', 'timeentrylistrow_stop_time_entry', 'trying to stop time entry', time_entry_id)
        resp = TimeEntryStopEndpoint(
            self.oauth2_mng.get_credential(),
            time_entry_id=time_entry_id
            ).patch()
        print('app', 'timeentrylistrow_stop_time_entry', time_entry_id, resp.status_code)
        print('app', 'timeentrylistrow_stop_time_entry', time_entry_id, resp.json())
        if resp.status_code == 200:
            listrowbox.render_stop_chronometer()

            # Updating Local data
            idx = -1
            for i, time_entry in enumerate(self.time_entries):
                if time_entry['id'] == resp.json()['id']:
                    idx = i
            self.time_entries[idx] = resp.json()
            listrowbox.data = resp.json()

    # Ops ---------------------------------------------------------------------

    def shift_week(self, shift):
        if shift == self.PREV_WEEK:
            self.selected_date = (self.selected_date - \
                timedelta(days=self.selected_date.weekday() + 1))
        elif shift == self.NEXT_WEEK:
            self.selected_date = (self.selected_date + \
                timedelta(days=7 - self.selected_date.weekday()))
        self.render_weekdays()
        self.lbox_timeentries.remove_all()
        self.spn_timeentries.start()
        self.spn_timeentries.show()

        CustomThread(
            target=self.shift_week_async,
            target_cb=self.shift_week_cb,
            ).start()

    def select_weekday(self, event_box, event_button):
        date_iso = event_box.get_name()
        for child in self.box_weekdays.get_children():
            if date_iso != child.get_name():
                child.set_normal()
        event_box.get_parent().set_bold()
        self.selected_date = datetime.strptime(date_iso,
                                               '%Y-%m-%dT%H:%M:%S.%f')
        self.spn_timeentries.start()
        self.spn_timeentries.show()
        self.render_time_entries()
        self.spn_timeentries.hide()
        self.spn_timeentries.stop()

    def get_user_avatar_img_as_pixbuf(self):
        import urllib
        url = self.user['avatar_url']
        response = urllib.request.urlopen(url)
        input_stream = Gio.MemoryInputStream.new_from_data(response.read(), None) 
        pixbuf = Pixbuf.new_from_stream(input_stream, None)
        return pixbuf

    def get_current_time_entry(_id):
        for time_entry in self.time_entries:
            if time_entry['id'] == _id:
                return time_entry

    def quit(self, *args):
        Gtk.main_quit()


def run():
    builder = Gtk.Builder()
    # builder.add_from_file('main2.glade')
    builder.add_objects_from_file(
        'main2.glade',
        ('window', 'popoverNewTimeEntry')
    )
    builder.connect_signals(AppHandler(builder))
    Gtk.main()


if __name__ == '__main__':
    run()
