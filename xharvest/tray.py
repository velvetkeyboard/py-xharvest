import gi
# gi.require_version("Gtk", "3.0")
# gi.require_version("WebKit2", "4.0")
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import AppIndicator3
from xharvest.data import get_app_icon_path


def get_menu(entries):
    menu = Gtk.Menu()

    for item in entries:
        menu_item_tupe = item[0]
        menu_item_name = item[1]
        activate_cb = item[2]
        if menu_item_tupe == 'item':
            menu_item = Gtk.MenuItem(menu_item_name)
        menu_item.show()
        if activate_cb:
            menu_item.connect('activate', activate_cb)
        menu.append(menu_item)

    return menu


class MainAppIndicator(object):
    def __init__(self, entries):
        icon_file_path = get_app_icon_path()
        self.ind = AppIndicator3.Indicator.new(
                "org.velvetkeyboard.xharvest",
                icon_file_path,
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
        self.ind.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon("indicator-messages-new")

        menu = get_menu(entries)
        menu.show()

        self.ind.set_menu(menu)
