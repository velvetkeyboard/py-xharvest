from datetime import date
from datetime import timedelta
from decimal import getcontext
from decimal import Decimal
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

from harvest.auth import PersonalAccessAuthClient
from harvest.api import TimeEntry
from harvest.api import TimeEntryStop
from harvest.api import TimeEntryRestart
from harvest.services import UsersAllAssignments
from harvest.services import Today
from harvest.services import SingleDayTimeEntries
from harvest.services import MonthTimeEntries
from harvest.services import CurrentUser

getcontext().prec = 3
COUNTER = 0
TIME_ENTRIES = []
TIMER_RUNNING = None


class TimeEntryOld(object):

    def __init__(self):
        self.description = ''
        self.clock_state = 'stopped'
        self.time = 0
        self.source_remove_id = 0
        self.label = None

    def clock_tick(self):
        print('another tick')
        if self.clock_state == 'running':
            self.time += 1
            print(self.time)
            self.label.set_text('{}:{:02d}'.format(
                int(self.time / 60),
                self.time % 60,
                ))
            self.source_remove_id = GLib.timeout_add_seconds(
                    1, self.clock_tick)

    def toggle_timer(self, button):
        print('toggling timer')
        global TIMER_RUNNING
        if self.clock_state == 'running':
            self.clock_state = 'stopped'
            GLib.source_remove(self.source_remove_id)
            self.source_remove_id = 0
            button.set_label('Start')
            TIMER_RUNNING = None

        elif self.clock_state == 'stopped':
            if TIMER_RUNNING:
                TIMER_RUNNING.clock_state = 'stopped'
                GLib.source_remove(TIMER_RUNNING.source_remove_id)
                TIMER_RUNNING.source_remove_id = 0
            self.clock_state = 'running'
            self.source_remove_id = GLib.timeout_add_seconds(
                    1, self.clock_tick)
            button.set_label('Stop')
            TIMER_RUNNING = self

    def edit_text(self, *args, **kwargs):
        print(args)

    def delete_entry(self, button):
        button.get_parent()


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

class App(object):

    def __init__(self):
        self.builder = Gtk.Builder()
        self.client_auth = PersonalAccessAuthClient()

    def start(self):
        self.builder.add_from_file("main.glade")
        self.builder.connect_signals(self)
        self.user = CurrentUser().get()
        print(self.user)
        # Initial Setup
        self.selected_date = date.today()
        self.sync_weekdays()
        self.builder.get_object("gtkLabelWeekNumber").set_label(f"{self.get_week_number()}")
        resp = Today().all()
        self.time_entries = resp['time_entries']
        self.sync_selected_date_timeentries()
        # import json
        # print(json.dumps(self.time_entries, indent=2))
        window = self.builder.get_object("main_window")
        self.get_month_hours()
        window.show_all()
        Gtk.main()

    def sync_weekdays(self):
        label_mon = self.builder.get_object("gtkLabelMonday")
        label_tue = self.builder.get_object("gtkLabelTuesday")
        label_wed = self.builder.get_object("gtkLabelWednesday")
        label_thu = self.builder.get_object("gtkLabelThursday")
        label_fri = self.builder.get_object("gtkLabelFriday")
        label_sat = self.builder.get_object("gtkLabelSaturday")
        label_sun = self.builder.get_object("gtkLabelSunday")
        today = self.selected_date
        self.dates = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
        label_mon.set_label(f"Mon\n{self.dates[0].day:02d}/{self.dates[0].month:02d}")
        label_tue.set_label(f"Tue\n{self.dates[1].day:02d}/{self.dates[1].month:02d}")
        label_wed.set_label(f"Wed\n{self.dates[2].day:02d}/{self.dates[2].month:02d}")
        label_thu.set_label(f"Thu\n{self.dates[3].day:02d}/{self.dates[3].month:02d}")
        label_fri.set_label(f"Fri\n{self.dates[4].day:02d}/{self.dates[4].month:02d}")
        label_sat.set_label(f"Sat\n{self.dates[5].day:02d}/{self.dates[5].month:02d}")
        label_sun.set_label(f"Sun\n{self.dates[6].day:02d}/{self.dates[6].month:02d}")

    def quit(self, *args):
        Gtk.main_quit()

    def create_new_entry(self, button):
        project_name = self.builder.get_object("gtkComboBoxTextNewTimeEntryProject").get_active_text()
        task_name = self.builder.get_object("gtkComboBoxTextNewTimeEntryTask").get_active_text()
        notes_buffer = self.builder.get_object("gtkComboBoxTextNewTimeEntryNotes").get_buffer()
        start_iter = notes_buffer.get_start_iter()
        end_iter = notes_buffer.get_end_iter()
        notes = notes_buffer.get_text(start_iter, end_iter, True)
        spent_date = self.selected_date.isoformat()
        hours = 0.01
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
        print(data)
        resp = TimeEntry(client=self.client_auth).post(data=data)
        print(resp.json())

    def show_new_timeentry_dialog(self, button):
        # builder = Gtk.Builder()
        # builder.add_from_file("new_time_entry.glade")
        newtimeentry_dialog = self.builder.get_object("gtkDialogNewTimeEntry")
        combobox_projects = self.builder.get_object("gtkComboBoxTextNewTimeEntryProject")

        self.project_assignments = {}

        resp = UsersAllAssignments(cfg='harvest.cfg').all()

        for assignment in resp:
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

        newtimeentry_dialog.run()

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

    # --(Time Entries Management)----------------------------------------------

    def toggle_hours_count(self, button):
        print('toggle_hours_count')
        time_entry_id = button.get_name()
        resp = TimeEntryUpdate(self.client, time_entry_id=time_entry_id).get()
        if resp.status_code == 200:
            if resp.json()['is_running']:
                resp = TimeEntryStop(self.client, time_entry_id=time_entry_id).patch()
            else:
                resp = TimeEntryRestart(self.client, time_entry_id=time_entry_id).patch()
            resp.json()['rounded_hours']

    def edit_timeentry(self, button):
        print('edit_timeentry')

    def delete_timeentry(self, event_box, event_button):
        print('delete_timeentry')
        print(event_box.get_name())

    # --(Week Calender Management)---------------------------------------------

    def get_week_number(self):
        return self.selected_date.isocalendar()[1]

    def get_last_week_timeentries(self, event_box, event_button):
        self.selected_date = self.selected_date - timedelta(days=7)
        self.sync_weekdays()

    def get_next_week_timeentries(self, event_box, event_button):
        self.selected_date = self.selected_date + timedelta(days=7)
        self.sync_weekdays()

    def get_month_hours(self):
        svc = MonthTimeEntries()
        svc.set_month(
            self.selected_date.year, self.selected_date.month)
        resp = svc.all()
        month_hours = Decimal(0)
        for entry in resp['time_entries']:
            month_hours += Decimal(entry['hours'])
        self.builder.get_object("gtkLabelMonthHours").set_label(str(month_hours))

    def get_monday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[0]
        self.sync_selected_date_timeentries()
        # label = event_box.get_child()

    def get_tuesday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[1]
        self.sync_selected_date_timeentries()

    def get_wednesday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[2]
        self.sync_selected_date_timeentries()

    def get_thursday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[3]
        self.sync_selected_date_timeentries()

    def get_friday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[4]
        self.sync_selected_date_timeentries()

    def get_saturday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[5]
        self.sync_selected_date_timeentries()

    def get_sunday_timeentries(self, event_box, event_button):
        self.selected_date = self.dates[6]
        self.sync_selected_date_timeentries()

    def sync_selected_date_timeentries(self):
        svc = SingleDayTimeEntries()
        svc.set_date(self.selected_date.isoformat())
        resp = svc.all()
        children = self.get_timeentry_list().get_children()#.remove_all()
        for child in children:
            self.get_timeentry_list().remove(child)
        day_hours = Decimal(0)
        for entry in resp['time_entries']:
            day_hours += Decimal(entry['hours'])
            self.insert_timeentry_widget(entry)
        self.builder.get_object("gtkLabelTodayHours").set_label(str(day_hours))

    def insert_timeentry_widget(self, timeentry_entity):
        builder = Gtk.Builder()
        builder.add_from_file("main.glade")
        builder.connect_signals(self)
        timeentry_wrapper = builder.get_object("gtkBoxTimeEntryWrapper")
        # notes = builder.get_object("gtkTextViewTimeEntryDescription")
        builder.get_object("gtkTextViewTimeEntryNotes").set_markup('<i>{}</i>'.format(timeentry_entity['notes']))
        # notes.set_monospace(True)
        # notes_buffer = notes.get_buffer()
        # notes_buffer.set_text('{}...'.format(timeentry_entity['notes'][:100]))
        hours = builder.get_object("gtkLabelTimer")
        hours.set_label(str(timeentry_entity['hours']))
        builder.get_object("gtkLabelTimeEntryTaskAndProjectName").set_markup(
            f"<b>{timeentry_entity['project']['name']} - {timeentry_entity['task']['name']}</b>")
        remove_timeentry = builder.get_object("gtkEventBoxRemoveTimeEntry")
        remove_timeentry.set_name(str(timeentry_entity['id']))

        toggle_timeentry = builder.get_object("gtkEventBoxToggleHoursCountTimeEntry")
        toggle_timeentry.set_name(str(timeentry_entity['id']))
        # builder.get_object("gtkLabelTimeEntryTaskAndProjectName").set_markup(
        #     f"<b>{timeentry_entity['project']['name']}</b>")
        # button_toggletimer = builder.get_object("gtkButtonToggleTimer")
        # delete_timeentry = builder.get_object("gtkEventBoxDeleteTimeEntry")

        # timeentry = TimeEntry()
        # timeentry.label = label_timer

        # desc.connect("focus", timeentry.edit_text)
        # button_toggletimer.connect("clicked", timeentry.toggle_timer)
        # remove_entry_fn = lambda btn, x: self.get_timeentry_list().remove(timeentry_wrapper.get_parent())

        # delete_timeentry.connect("button-release-event", remove_entry_fn)

        # timeentrywrapper = builder.get_object("gtkBoxTimeEntryWrapper")
        self.get_timeentry_list().add(timeentry_wrapper)


if __name__ == '__main__':
    app = App()
    app.start()
