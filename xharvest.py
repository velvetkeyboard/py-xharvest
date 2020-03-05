from decimal import getcontext
from decimal import Decimal
import gi
from gi.repository import Gtk

gi.require_version("Gtk", "3.0")

from gi.repository import GObject
from gi.repository import GLib

getcontext().prec = 2
COUNTER = 0
TIME_ENTRIES = []
TIMER_RUNNING = None


class TimeEntry(object):

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


class Handler(object):

    def quit(self, *args):
        Gtk.main_quit()

    def hello(self, button):
        print("Hello World!")
        builder = Gtk.Builder()
        # builder.add_objects_from_file("time_entry.xml", ("gtkBoxTimeEntryWrapper",))
        builder.add_objects_from_file("time_entry.xml")
        listbox_timeentries = builder.get_object("gtkListBoxTimeEntries")
        # listbox_timeentries = builder.get_object("gtkScrolledWindowTimeEntries")
        # timeentrywrapper = builder.get_object("gtkBoxTimeEntryWrapper")
        button_toggletimer = builder.get_object("gtkButtonToggleTimer")
        timeentry = TimeEntry()
        button_toggletimer.connect("clicked", timeentry.toggle_timer)
        listbox_timeentries.add(timeentrywrapper)


class App(object):

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("main.xml")
        self.builder.connect_signals(self)

    def start(self):
        window = self.builder.get_object("window1")
        window.show_all()
        Gtk.main()

    def quit(self, *args):
        Gtk.main_quit()

    def get_timeentry_list(self):
        return self.builder.get_object("gtkListBoxTimeEntries")

    def hello(self, button):
        builder = Gtk.Builder()
        builder.add_from_file("time_entry.xml")

        timeentry_wrapper = builder.get_object("gtkBoxTimeEntryWrapper")
        desc = builder.get_object("gtkTextViewTimeEntryDescription")
        label_timer = builder.get_object("gtkLabelTimer")
        button_toggletimer = builder.get_object("gtkButtonToggleTimer")
        delete_timeentry = builder.get_object("gtkEventBoxDeleteTimeEntry")

        timeentry = TimeEntry()
        timeentry.label = label_timer

        desc.connect("focus", timeentry.edit_text)
        button_toggletimer.connect("clicked", timeentry.toggle_timer)
        remove_entry_fn = lambda btn, x: self.get_timeentry_list().remove(timeentry_wrapper.get_parent())

        delete_timeentry.connect("button-release-event", remove_entry_fn)

        timeentrywrapper = builder.get_object("gtkBoxTimeEntryWrapper")
        self.get_timeentry_list().add(timeentrywrapper)

# builder.add_objects_from_file("time_entry.xml", ("gtkBoxTimeEntryWrapper",))

# help(listbox_timeentries)
#timeentrywrapper = builder.get_object("gtkBoxTimeEntryWrapper")
#listbox_timeentries.add(timeentrywrapper)

app = App()
app.start()
