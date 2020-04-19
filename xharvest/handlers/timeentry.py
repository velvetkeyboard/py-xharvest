from harvest.endpoints import TimeEntryStopEndpoint
from harvest.endpoints import TimeEntryRestartEndpoint
from xharvest.threads import *
from xharvest.models import Hour
from xharvest.factories import *
from xharvest.handlers.base import Handler
from xharvest.handlers.timeentryform import TimeEntryFormHandler


class TimeEntryHandler(Handler):

    CHRONOMETER_DELAY = 37

    def __init__(self, time_entry_id):
        super(TimeEntryHandler, self).__init__()
        self.hour = None
        self.time_entry_id = time_entry_id
        self.source_remove_id = None
        self.custom_signals.connect(
                'time_entry_restarted', self.on_time_entry_restarted)

    def get_time_entry(self):
        return self.time_entries.get_by_id(self.time_entry_id)

    def on_time_entry_restarted(self, gobj, to_be_restarted_time_entry_id):
        if self.time_entry_id != to_be_restarted_time_entry_id and \
            self.get_time_entry()['is_running']:
            GtkThread(
                target=self.stop_chronometer,
                target_cb=self.stop_chronometer_cb).start()

    def on_show_edit_time_entry_form(self, event_box, event_button):
        time_entry = self.get_time_entry()
        handler = TimeEntryFormHandler(self.time_entry_id)
        data = {
            'time_entry': time_entry,
            'assignments': self.assignments.data,
        }
        popover = TimeEntryFormFactory(handler, data).build()
        popover.set_relative_to(event_box)
        popover.popup()

    def on_toggle_chronometer(self, event_box, event_button):
        time_entry = self.time_entries.get_by_id(self.time_entry_id)
        if time_entry['is_running']:
            print(f'time entry #{self.time_entry_id} will stop running now')
            GtkThread(
                target=self.stop_chronometer,
                target_cb=self.stop_chronometer_cb).start()
        else:
            print(f'time entry #{self.time_entry_id} will start to running now')
            self.custom_signals.emit('time_entry_restarted', self.time_entry_id)
            GtkThread(
                target=self.start_chronometer,
                target_cb=self.start_chronometer_cb).start()

    def start_chronometer(self):
        endpoint = TimeEntryRestartEndpoint(
                self.oauth2_mng.get_credential(),
                time_entry_id=self.time_entry_id)
        resp = endpoint.patch()
        if resp.status_code == 200:
            self.get_time_entry()['is_running'] = resp.json()['is_running']

    def stop_chronometer(self):
        endpoint = TimeEntryStopEndpoint(
                self.oauth2_mng.get_credential(),
                time_entry_id=self.time_entry_id)
        resp = endpoint.patch()
        if resp.status_code == 200:
            self.get_time_entry()['is_running'] = resp.json()['is_running']
            self.get_time_entry()['hours'] = resp.json()['hours']

    @gtk_thread_class_cb
    def start_chronometer_cb(self, thread=None):
        self.spinner.start()
        self.img_toggle.set_from_icon_name('gtk-media-pause', 1)
        self.source_remove_id = GLib.timeout_add_seconds(
            self.CHRONOMETER_DELAY, self.chronometer)

    @gtk_thread_class_cb
    def stop_chronometer_cb(self, thread=None):
        self.spinner.stop()
        self.img_toggle.set_from_icon_name('gtk-media-play', 1)
        self.update_hours_label(self.get_time_entry()['hours'])
        if self.source_remove_id:
            GLib.source_remove(self.source_remove_id)
            self.source_remove_id = None

    def chronometer(self):
        if not self.hour:
            self.hour = Hour(self.get_time_entry()['hours'])
        if self.get_time_entry()['is_running']:
            print(f"time entry #{self.time_entry_id} - tick")
            self.hour.add_sec(self.CHRONOMETER_DELAY)
            self.update_hours_label(self.hour.as_harvest())
            self.source_remove_id = GLib.timeout_add_seconds(
                self.CHRONOMETER_DELAY, self.chronometer)
        else:
            print(f"time entry #{self.time_entry_id} - stop ticking")
            if self.source_remove_id:
                GLib.source_remove(self.source_remove_id)
                self.source_remove_id = None

    def update_hours_label(self, val):
        val = float(val)
        self.label_hours.set_markup(f"<b>{val:.2f}</b>")

