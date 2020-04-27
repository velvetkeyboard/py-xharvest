from gi.repository import Gtk
from gi.repository import Gdk
from xharvest.data import get_img_path
from xharvest.threads import GtkThread
from xharvest.handlers.base import Handler
from xharvest.handlers.timeentries import TimeEntriesHandler
from xharvest.handlers.week import WeekHandler
from xharvest.handlers.main_headerbar import MainHeaderBarHandler
from xharvest.handlers.settings import SettingsHandler
from xharvest.handlers.timeentry import TimeEntryFormHandler
from xharvest.handlers.login import LoginHandler


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
        # Attaching fixed widgets
        self.vp_week.add(WeekHandler().get_root_widget())
        self.viewport.add(TimeEntriesHandler().get_root_widget())
        self.get_root_widget().set_icon_from_file(get_img_path("xharvest.png"))
        if not self.oauth2.is_access_token_expired():
            self.fetch_base_data()

    def bind_signals(self):
        self.time_entries.connect(
            "time_entries_were_rendered", self.on_time_entries_were_rendered
        )
        self.time_entries.connect(
            "data_update_bgn", self.on_time_entries_data_being_updated
        )
        self.oauth2.connect("user_authenticated", self.on_user_authenticated)
        self.oauth2.connect("user_signout", self.on_user_signout)

    # ----------------------------------------------------------------[Helpers]

    def fetch_base_data(self):
        '''
        Description:
            Yes. We are blocking on purpose to avoid user trying interacting
            with some part of the UI and see no reaction. We will slowly move
            the parts to be more and more asynchronous.
        '''
        self.user.fetch_data()
        self.assignments.fetch_data()
        GtkThread(target=self.time_entries.fetch_data).start()

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

    def on_quit(self, *args):
        Gtk.main_quit()

    # ----------------------------------------------------------[Model Signals]

    def on_user_authenticated(self, gobj):
        self.fetch_base_data()
        self.get_root_widget().show()

    def on_user_signout(self, gobj):
        self.get_root_widget().hide()
        LoginHandler().get_root_widget().show_all()

    def on_time_entries_were_rendered(self, gobj):
        self.spin.stop()

    def on_time_entries_data_being_updated(self, gobj):
        self.spin.start()
