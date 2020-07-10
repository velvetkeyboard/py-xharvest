from datetime import datetime
from gi.repository import Gtk
from gi.repository import Gdk
from xharvest.data import get_img_path
from xharvest.auth import AuthenticationManager
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb
from xharvest.models import Shortcuts
from xharvest.handlers.base import Handler
from xharvest.handlers.timeentries import TimeEntriesHandler
from xharvest.handlers.week import WeekHandler
from xharvest.handlers.main_headerbar import MainHeaderBarHandler
from xharvest.handlers.settings import SettingsHandler
from xharvest.handlers.timeentry import TimeEntryFormHandler
from xharvest.handlers.login import LoginHandler
from xharvest.tray import MainAppIndicator


class MainWindowHandler(Handler):

    MASK_BOOTING = Gdk.WindowState.WITHDRAWN | Gdk.WindowState.FOCUSED

    def bind_data(self):
        # You need to attach Headerbar before the Window is shown
        self.get_root_widget().set_titlebar(
            MainHeaderBarHandler().get_root_widget())
        # Most reused Widgets
        self.spin = self.builder.get_object("spinner")
        self.box = self.builder.get_object("box")
        self.vp_week = self.builder.get_object("viewport_week")
        self.viewport = self.builder.get_object("viewport_time_entries")
        self.evbox_new_timeentry = self.get_widget("evbox_new_timeentry")
        # Attaching fixed widgets
        self.vp_week.add(WeekHandler().get_root_widget())
        self.viewport.add(TimeEntriesHandler().get_root_widget())
        self.get_root_widget().set_icon_from_file(get_img_path("xharvest.png"))
        if AuthenticationManager().is_user_authenticated():
            self.fetch_base_data()
        self.app_ind = MainAppIndicator([
            ('item', 'Show', self.on_show),
            ('item', 'Quit', lambda m: Gtk.main_quit()),
            ])

    def bind_signals(self):
        self.get_root_widget().connect("delete-event", self.on_quit)
        self.time_entries.connect(
            "time_entries_were_rendered",
            lambda gobj: self.spin.stop()
            )
        self.time_entries.connect(
            "data_update_bgn",
            lambda gobj: self.spin.start()
            )
        self.auth_flow.connect("user_authenticated", self.on_user_authenticated)
        self.auth_flow.connect("user_signout", self.on_user_signout)

        self.bind_accel_groups()

    def bind_accel_groups(self):
        self.ag_1 = self.preferences.get_accel_group(
                Shortcuts.SHOW_TIME_ENTRY_FORM,
                self.on_show_time_entry_form_kb,
                )
        self.ag_2 = self.preferences.get_accel_group(
                Shortcuts.SHOW_TODAYS_ENTRIES,
                self.on_back_to_today_kb,
                )
        # self.ag_3 = self.preferences.get_accel_group(
        #         Shortcuts.SHOW_TIME_SUMMARY,
        #         self.on_show_time_summary_kb,
        #         )
        # Re-attaching
        self.get_root_widget().add_accel_group(self.ag_1)
        self.get_root_widget().add_accel_group(self.ag_2)
        # self.get_root_widget().add_accel_group(self.ag_3)

    # ----------------------------------------------------------------[Helpers]

    def fetch_base_data(self):
        '''
        Description:
            Yes. We are blocking on purpose to avoid user trying interacting
            with some part of the UI and see no reaction. We will slowly move
            the parts to be more and more asynchronous.
        '''
        self.user.sync_data()
        self.assignments.sync_data()
        self.time_entries.emit('data_update_bgn')
        GtkThread(
            target=self.time_entries.sync_data,
            target_cb=gtk_thread_cb(
                lambda t: self.time_entries.emit('data_update_end')
                ),
            ).start()

    # -------------------------------------------------------[Standard Signals]

    def on_evbox_new_timeentry_button_press_event(self, ev_box, ev_btn):
        if self.assignments.data:
            w = TimeEntryFormHandler().get_root_widget()
            w.set_relative_to(ev_box)
            w.popup()

    def on_evbox_show_settings_button_press_event(self, ev_box, gdk_ev_btn):
        if self.user.data:
            w = SettingsHandler().get_root_widget()
            w.set_relative_to(ev_box)
            w.show_all()
            w.popup()

    # FIXME show/hide is breaking the main window
    def on_show(self, *args):
        self.get_root_widget().deiconify()
        self.get_root_widget().present()

    def on_quit(self, *args):
        if self.preferences.get_minimize_to_tray_icon():
            self.get_root_widget().hide()
            return True
        else:
            Gtk.main_quit()

    # ----------------------------------------------------------[Model Signals]

    def on_show_time_entry_form_kb(self, *args):
        self.on_evbox_new_timeentry_button_press_event(
            self.evbox_new_timeentry,
            None,
            )

    def on_back_to_today_kb(self, *args):
        self.week.set_selected_date(datetime.now())
        self.week.emit("selected_date_changed")
        self.time_entries.date_obj = self.week.get_selected_date()
        self.time_entries.emit('data_update_bgn')
        GtkThread(
            target=self.time_entries.sync_data,
            target_cb=gtk_thread_cb(
                lambda t: self.time_entries.emit('data_update_end')
                ),
            ).start()

    def on_user_authenticated(self, gobj):
        self.fetch_base_data()
        self.get_root_widget().show()

    def on_user_signout(self, gobj):
        self.get_root_widget().hide()
        # LoginHandler().get_root_widget().show_all()
        LoginHandler().get_root_widget().present()
