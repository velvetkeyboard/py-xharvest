from gi.repository import GLib
from harvest.endpoints import TimeEntryStopEndpoint
from harvest.endpoints import TimeEntryRestartEndpoint
from xharvest.logger import logger
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_method_cb
from xharvest.models import Hour
from xharvest.handlers.base import Handler
from xharvest.handlers.timeentryform import TimeEntryFormHandler


class TimeEntryHandler(Handler):

    CHRONOMETER_DELAY = 37

    template = "time_entry"
    root_widget = "box_time_entry"

    def __init__(self, time_entry):
        self.hour = None
        self.data = time_entry
        self.time_entry_id = time_entry["id"]
        self.source_remove_id = None
        super(TimeEntryHandler, self).__init__()

    def bind_data(self):
        proj_name = f'<b>{self.data["project"]["name"]}</b>'
        if self.data["project"]["code"]:
            proj_code = self.data["project"]["code"]
            proj_label = f'<b>[{proj_code}] {proj_name}</b>'
        else:
            proj_label = proj_name

        self.builder.get_object("labelTimeEntryNotes").set_markup(
            f'<i>{self.data["notes"]}</i>'
        )
        self.builder.get_object("labelTimeEntryProject").set_markup(proj_label)
        self.builder.get_object("labelTimeEntryTask").set_markup(
            f"<b>{self.data['task']['name']}</b>"
        )
        self.builder.get_object("labelTimeEntryHours").set_markup(
            f"<b>{self.data['hours']:02.02f}</b>"
        )
        # self.builder.get_object('eventBoxTimeEntryEdit')\
        #             .set_name(str(self.data['id']))

        self.spinner = self.builder.get_object("spinnerTimeEntry")
        self.eb_toggle = self.builder.get_object(
            "eventBoxTimeEntryToggleRunning")
        self.img_toggle = self.builder.get_object(
            "imageTimeEntryToggleRunning")
        self.label_hours = self.builder.get_object("labelTimeEntryHours")

        if self.data["is_running"]:
            self.start_chronometer_cb()

    def bind_signals(self):
        self.time_entries.connect(
            "time_entry_restarted", self.on_time_entry_restarted
        )
        self.time_entries.connect("time_entry_saved", self.on_time_entry_saved)

    # ----------------------------------------------------------------[Helpers]

    def get_time_entry(self):
        return self.time_entries.get_by_id(self.time_entry_id)

    # -----------------------------------------------------------[Model Events]

    def on_time_entry_restarted(self, gobj, rst_time_entry_id):
        is_running = self.get_time_entry()["is_running"]
        if self.time_entry_id != rst_time_entry_id and is_running:
            GtkThread(
                target=self.stop_chronometer,
                target_cb=self.stop_chronometer_cb
            ).start()

    def on_time_entry_saved(self, gobj, time_entry_id):
        if int(time_entry_id) == int(self.time_entry_id):
            self.data = self.time_entries.get_by_id(time_entry_id)
            self.bind_data()

    # ------------------------------------------------------------[Core Events]

    def on_show_edit_form(self, ev_box, gdk_ev_btn):
        if self.assignments.data:
            handler = TimeEntryFormHandler(self.time_entry_id)
            popover = handler.get_root_widget()
            popover.set_relative_to(ev_box)
            popover.popup()

    def on_toggle_chronometer(self, ev_box, gdk_ev_btn):
        time_entry = self.time_entries.get_by_id(self.time_entry_id)
        if time_entry["is_running"]:
            GtkThread(
                target=self.stop_chronometer,
                target_cb=self.stop_chronometer_cb,
                ).start()
        else:
            self.time_entries.emit(
                "time_entry_restarted", self.time_entry_id)
            GtkThread(
                target=self.start_chronometer,
                target_cb=self.start_chronometer_cb
                ).start()

    def start_chronometer(self):
        endpoint = TimeEntryRestartEndpoint(
            self.oauth2.get_credential(), time_entry_id=self.time_entry_id
        )
        resp = endpoint.patch()
        if resp.status_code == 200:
            self.get_time_entry()["is_running"] = resp.json()["is_running"]

    def stop_chronometer(self):
        endpoint = TimeEntryStopEndpoint(
            self.oauth2.get_credential(), time_entry_id=self.time_entry_id
        )
        resp = endpoint.patch()
        if resp.status_code == 200:
            self.get_time_entry()["is_running"] = resp.json()["is_running"]
            self.get_time_entry()["hours"] = resp.json()["hours"]

    @gtk_thread_method_cb
    def start_chronometer_cb(self, thread=None):
        self.spinner.start()
        self.img_toggle.set_from_icon_name("gtk-media-pause", 1)
        self.source_remove_id = GLib.timeout_add_seconds(
            self.CHRONOMETER_DELAY, self.chronometer
        )

    @gtk_thread_method_cb
    def stop_chronometer_cb(self, thread=None):
        self.spinner.stop()
        self.img_toggle.set_from_icon_name("gtk-media-play", 1)
        self.update_hours_label(self.get_time_entry()["hours"])
        if self.source_remove_id:
            GLib.source_remove(self.source_remove_id)
            self.source_remove_id = None

    def chronometer(self):
        if not self.hour:
            self.hour = Hour(self.get_time_entry()["hours"])
        if self.get_time_entry()["is_running"]:
            logger.debug(f"time entry #{self.time_entry_id} - tick")
            self.hour.add_sec(self.CHRONOMETER_DELAY)
            self.update_hours_label(self.hour.as_harvest())
            self.source_remove_id = GLib.timeout_add_seconds(
                self.CHRONOMETER_DELAY, self.chronometer
            )
        else:
            logger.debug(f"time entry #{self.time_entry_id} - stop ticking")
            if self.source_remove_id:
                GLib.source_remove(self.source_remove_id)
                self.source_remove_id = None

    def update_hours_label(self, val):
        val = float(val)
        self.label_hours.set_markup(f"<b>{val:.2f}</b>")
