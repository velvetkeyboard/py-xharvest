from gi.repository import Gtk
from xharvest.handlers.base import Handler
from xharvest.handlers.about import AboutHandler


class SettingsHandler(Handler):
    def bind_data(self):
        self.get_widget("label_user_fullname")\
            .set_markup(self.user.get_full_name())
        self.get_widget("label_user_email").set_markup(self.user.data["email"])
        self.get_widget("label_user_avatar").set_from_pixbuf(
            self.user.get_avatar_img_as_pixbuf()
        )

    def on_go_to_my_account(self, *args):
        acc_id = self.user.data['id']
        Gtk.show_uri(None, f"https://id.getharvest.com/accounts/{acc_id}", 1)

    def on_popover_settings_closed(self, *args):
        self.get_root_widget().destroy()

    def on_visit_help_center(self, *args):
        Gtk.show_uri(None, "https://help.getharvest.com/", 1)

    def on_about(self, *args):
        AboutHandler().get_root_widget().show_all()

    def on_signout(self, ev_box, gdk_ev_btn):
        self.oauth2.wipe()
        self.oauth2.emit("user_signout")

    def on_quit(self, *args):
        Gtk.main_quit()
