from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb
from xharvest.models.timesummary import TimeSummary
from xharvest.handlers.base import Handler


class TimeSummaryHandler(Handler):

    # template = 'time_summary'

    def bind_signals(self):
        self.preferences.connect(
                'show_time_summary', self.on_show_time_summary_kb)
        self.time_summary = TimeSummary()
        self.time_summary.connect("data_update_end", self.render)
        self.fetch_time_summary()

    def render(self, gobj=None):
        self.get_widget("labelTimeSummaryHoursToday").set_label(
            f"{self.time_summary.today:02.02f}"
        )
        self.get_widget("labelTimeSummaryHoursYesterday").set_label(
            f"{self.time_summary.yesterday:02.02f}"
        )
        self.get_widget("labelTimeSummaryHoursWeek").set_label(
            f"{self.time_summary.week:02.02f}"
        )
        self.get_widget("labelTimeSummaryHoursMonth").set_label(
            f"{self.time_summary.month:02.02f}"
        )
        self.get_widget("spinner").stop()
        self.get_widget("spinner").hide()
        self.get_widget("grid").set_visible(True)

    def fetch_time_summary(self):
        GtkThread(
            target=self.time_summary.sync_data,
            args=(self.week.get_selected_date(),),
            target_cb=gtk_thread_cb(
                lambda t: self.time_summary.emit("data_update_end")
            ),
        ).start()

    def on_show_time_summary_kb(self, gobj):
        self.fetch_time_summary()

    def on_root_closed(self, pop):
        pop.destroy()
