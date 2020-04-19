#import pkg_resources
from gi.repository import Gtk
from xharvest.data import GLADE_FILE

#GLADE_FILE = pkg_resources.resource_filename('xharvest', 'glade/main2.glade')


class Factory(object):
    glade_file = GLADE_FILE
    widget_ids = ()
    root_widget_name = ''

    def __init__(self, handler, data=None):
        self.handler = handler
        self.data = data

    def get_root_widget(self):
        return self.builder.get_object(self.root_widget_name)

    def build(self):
        self.builder = Gtk.Builder()
        self.builder.add_objects_from_file(self.glade_file, self.widget_ids)
        self.builder.connect_signals(self.handler)
        self.handler.set_builder(self.builder)
        self.bind()
        return self.get_root_widget()

    def bind(self):
        raise NotImplemented

