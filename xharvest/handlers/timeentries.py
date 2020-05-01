from datetime import datetime
from operator import itemgetter
from gi.repository import GLib
from xharvest.threads import GtkThread
from xharvest.utils import remove_all_children
from xharvest.handlers.base import Handler
from xharvest.handlers.timeentry import TimeEntryHandler


class TimeEntriesHandler(Handler):
    template = "time_entries"
    root_widget = "lbox_timeentries"

    PULLING_DELAY = 37

    def bind_signals(self):
        self.time_entries.connect("data_update_end", self.render)
        self.week.connect("selected_date_changed", self.render)

    def render(self, gobj):
        lbox = self.get_widget("lbox_timeentries")
        remove_all_children(lbox)
        self.time_entries.data.sort(key=itemgetter("created_at"))
        for time_entry in self.time_entries.data:
            spent_date = time_entry["spent_date"]
            spent_date = datetime.strptime(spent_date, "%Y-%m-%d").date()
            if self.week.get_selected_date().date() == spent_date:
                lbox.add(TimeEntryHandler(time_entry).get_root_widget())
        lbox.show_all()
        self.time_entries.emit("time_entries_were_rendered")
        self.source_remove_id = GLib.timeout_add_seconds(
            self.PULLING_DELAY,
            lambda : GtkThread(target=self.time_entries.fetch_data).start(),
            )
 
