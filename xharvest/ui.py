import pkg_resources
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk
from gi.repository.WebKit2 import WebView
from gi.repository.WebKit2 import Settings
from xharvest.handlers import *
from xharvest.data import GLADE_FILE

#GLADE_FILE = pkg_resources.resource_filename(__name__, 'data/glade/main2.glade')


def main():
    builder = Gtk.Builder()
    builder.add_objects_from_file(
        GLADE_FILE,
        ('window',)
    )
    builder.connect_signals(MainHandler(builder))
    builder.get_object('window').show_all()
    Gtk.main()

