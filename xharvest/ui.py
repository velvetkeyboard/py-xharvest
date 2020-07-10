import gi
gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository.WebKit2 import WebView
from gi.repository.WebKit2 import Settings
from xharvest.handlers.main import MainWindowHandler
from xharvest.handlers.login import LoginHandler
from xharvest.auth import AuthenticationManager
from xharvest.data import get_css_path


def load_css():
    style_provider = Gtk.CssProvider()

    css = open(get_css_path("main"), "rb")
    css_data = css.read()
    css.close()

    style_provider.load_from_data(css_data)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )


def main():
    load_css()
    handler = MainWindowHandler()
    handler.get_root_widget().show_all()

    if not AuthenticationManager().is_user_authenticated():
        LoginHandler().get_root_widget().show_all()
        handler.get_root_widget().hide()

    Gtk.main()
