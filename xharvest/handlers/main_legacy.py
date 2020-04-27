from datetime import datetime
from operator import itemgetter

from gi.repository import Gtk
from gi.repository import Gdk

from xharvest.threads import *
from xharvest.models import *
from xharvest.factories import *
from xharvest.handlers.base import Handler
from xharvest.handlers.weekday import WeekDayHandler
from xharvest.handlers.timeentry import TimeEntryHandler
from xharvest.handlers.timeentryform import TimeEntryFormHandler
from xharvest.handlers.settings import SettingsHandler
from xharvest.handlers.authentication import AuthHandler


class MainHandler(Handler):

    mask_booting = Gdk.WindowState.WITHDRAWN | Gdk.WindowState.FOCUSED

    def __init__(self, builder):
        self.builder = builder
        self.spinner = self.builder.get_object('spinnerTimeEntries')

    def initial_setup(self):
        # self.oauth2_mng = OAuth2CredentialManager()
        self.week.set_selected_date(datetime.now())
        self.render_week_days()

        if not self.oauth2_mng.is_access_token_expired():
            self.week.connect(
                    'selected_date_changed', self.on_selected_date_changed)
            self.time_entries.connect(
                    'time_entry_saved', self.on_time_entry_saved)
            self.time_entries.connect(
                    'time_entry_deleted', self.on_time_entry_deleted)
            self.custom_signals.connect(
                    'user_signout', self.on_user_signout)
            self.start_spinner()
            self.user.oauth2 = self.oauth2_mng.get_credential()
            self.assignments.oauth2 = self.oauth2_mng.get_credential()
            self.time_entries.oauth2 = self.oauth2_mng.get_credential()
            self.time_entries.date_obj = self.week.get_selected_date()
            # self.user.fetch_data()
            GtkThread(target=self.user.fetch_data).start()
            GtkThread(target=self.assignments.fetch_data).start()
            GtkThread(target=self.time_entries.fetch_data,
                      target_cb=self.render_time_entries).start()
        else:
            w = AuthFactory(AuthHandler(), self.oauth2_mng).build()
            w.show_all()

    def start_spinner(self):
        self.spinner.show()
        self.spinner.start()

    def stop_spinner(self):
        self.spinner.hide()
        self.spinner.stop()

    def get_titlebar(self):
        widget = MainTitleBarFactory().build()
        return widget

    def on_window_state_event(self, window, event_window_state):
        changed_mask = event_window_state.changed_mask
        window_state = event_window_state.new_window_state
        if window_state == Gdk.WindowState.FOCUSED and \
            self.mask_booting == changed_mask:
            win = self.get_widget('window')
            win.set_titlebar(self.get_titlebar())
            self.custom_signals.connect(
                    'user_authenticated', self.initial_setup)
            self.initial_setup()

    def render_week_days(self):
        box = self.builder.get_object('boxWeekDays')
        self.remove_all_children(box)
        for day in self.week.days:
            widget = WeekDayFactory(WeekDayHandler(), day).build()
            widget.show_all()
            box.add(widget)
        self.update_window_title()

    @gtk_thread_class_cb
    def render_time_entries(self, thread=None):
        lbox = self.builder.get_object('listBoxTimeEntries')
        self.time_entries.data.sort(key=itemgetter('created_at'))
        for c in lbox.get_children():
            lbox.remove(c)
        for time_entry in self.time_entries.data:
            if self.week.get_selected_date().date() == \
                datetime.strptime(time_entry['spent_date'], '%Y-%m-%d').date():
                w = TimeEntryFactory(
                        TimeEntryHandler(time_entry['id']),
                        time_entry).build()
                lbox.add(w)
        lbox.show_all()
        self.stop_spinner()

    def update_window_title(self):
        label = self.builder.get_object('labelSelectedDateFullDesc')
        label.set_markup(self.week.selected_date.strftime('%A, %d %B'))

    def on_time_entry_saved(self, *args, **kwargs):
        self.render_time_entries()

    def on_time_entry_deleted(self, *args, **kwargs):
        self.render_time_entries()

    def on_selected_date_changed(self, week, iso_date):
        self.render_time_entries()

    def on_back_home(self, ev_box, ev_btn):
        self.week.set_selected_date(datetime.now())
        self.render_week_days()
        self.render_time_entries()
        self.update_window_title()

    def get_last_week_timeentries(self, *args):
        self.week.shift_prev_week()
        self.render_week_shift()

    def get_next_week_timeentries(self, *args):
        self.week.shift_next_week()
        self.render_week_shift()

    def render_week_shift(self):
        self.time_entries.date_obj = self.week.get_selected_date()
        self.time_entries.fetch_data()
        self.render_week_days()
        self.render_time_entries()

    def on_show_new_time_entry_form(self, event_box, event_button):
        data = {
            'time_entry': None,
            'assignments': self.assignments.data,
            #'relative_widget': event_box,
        }
        popover = TimeEntryFormFactory(TimeEntryFormHandler(), data).build()
        popover.set_relative_to(event_box)
        popover.popup()

    def on_show_settings_menu(self, ev_box, ev_btn):
        handler = SettingsHandler()
        data = {'user': self.user.data}
        win = SettingsFactory(handler, data).build()
        win.show_all()

    def on_user_signout(self, gobj):
        self.oauth2_mng.wipe()
        self.time_entries.data = []
        lbox = self.builder.get_object('listBoxTimeEntries')
        for c in lbox.get_children():
            lbox.remove(c)
        self.initial_setup()

    def on_quit(self, *args):
        Gtk.main_quit()
