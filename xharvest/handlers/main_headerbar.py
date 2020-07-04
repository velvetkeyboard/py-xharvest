from datetime import datetime
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb
from xharvest.handlers.base import Handler
from xharvest.handlers.time_summary import TimeSummaryHandler


class MainHeaderBarHandler(Handler):

    template = "main_headerbar"
    root_widget = "headerbar_main"

    def bind_signals(self):
        self.week.connect(
            "selected_date_changed", self.on_selected_date_changed)

    def bind_data(self):
        self.render(self.week.get_selected_date().strftime("%A, %d %B"))

    # ----------------------------------------------------------------[Helpers]

    def render(self, text):
        self.get_widget("labelSelectedDateFullDesc").set_markup(text)

    # -------------------------------------------------------[Standard Signals]

    def on_back_to_today(self, ev_box, ev_btn):
        self.week.set_selected_date(datetime.now())
        self.week.emit("selected_date_changed")
        self.time_entries.date_obj = self.week.get_selected_date()
        GtkThread(
            target=self.time_entries.sync_data,
            target_cb=gtk_thread_cb(
                lambda t: self.time_entries.emit("data_update_end")
            ),
            ).start()

    def on_show_time_summary(self, ev_box, ev_btn):
        widget = TimeSummaryHandler().get_root_widget()
        widget.set_relative_to(ev_box)
        widget.popup()

    # ----------------------------------------------------------[Model Signals]

    def on_selected_date_changed(self, gobj):
        self.render(self.week.get_selected_date().strftime("%A, %d %B"))
