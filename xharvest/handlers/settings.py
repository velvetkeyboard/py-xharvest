from gi.repository import Gtk
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb
from xharvest.auth import AuthenticationManager
from xharvest.handlers.base import Handler
from xharvest.handlers.about import AboutHandler
from xharvest.handlers.preferences import PreferencesHandler


class SettingsHandler(Handler):
    def bind_data(self):
        self.get_widget("label_user_fullname")\
            .set_markup(self.user.get_full_name())
        self.get_widget("label_user_email").set_markup(self.user.data["email"])
        self.get_widget("label_user_avatar").set_from_pixbuf(
            self.user.get_avatar_img_as_pixbuf()
        )
        self.get_widget("label_user_avatar").set_from_pixbuf(
            self.user.get_avatar_img_as_pixbuf(),
            )
        GtkThread(
            target=self.user.download_user_avatar,
            target_cb=gtk_thread_cb(
                lambda t: self.user.emit("avatar_download_end")),
            ).start()

    def bind_signals(self):
        self.user.connect(
            "avatar_download_end", self.on_avatar_download_end)

    def on_avatar_download_end(self, gobj):
        self.get_widget("label_user_avatar").set_from_pixbuf(
            self.user.get_avatar_img_as_pixbuf(),
            )

    def on_go_to_my_account(self, *args):
        acc_id = self.user.data['id']
        Gtk.show_uri(None, f"https://id.getharvest.com/accounts/{acc_id}", 1)

    def on_show_preferences(self, *args):
        PreferencesHandler().get_root_widget().show_all()

    def on_popover_settings_closed(self, *args):
        self.get_root_widget().destroy()

    def on_visit_help_center(self, *args):
        Gtk.show_uri(None, "https://help.getharvest.com/", 1)

    def on_about(self, *args):
        AboutHandler().get_root_widget().show_all()

    def on_signout(self, ev_box, gdk_ev_btn):
        AuthenticationManager().wipe()
        self.auth_flow.emit("user_signout")

    def on_quit(self, *args):
        Gtk.main_quit()
