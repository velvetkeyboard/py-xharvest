from xharvest.utils import remove_all_children
from xharvest.threads import GtkThread
from xharvest.threads import gtk_thread_cb
from xharvest.handlers.base import Handler
from xharvest.handlers.weekday import WeekDayHandler


class WeekHandler(Handler):
    template = "week"
    root_widget = "box_week"

    def bind_data(self):
        self.week.gen_days()
        self.box = self.builder.get_object("boxWeekDays")
        self.on_selected_date_changed(None)

    def bind_signals(self):
        self.week.connect(
            "selected_date_changed", self.on_selected_date_changed)

    def fetch_new_time_entries(self):
        self.week.emit("selected_date_changed")
        self.time_entries.date_obj = self.week.get_selected_date()
        self.time_entries.emit('data_update_bgn')
        GtkThread(
            target=self.time_entries.sync_data,
            target_cb=gtk_thread_cb(
                lambda t: self.time_entries.emit('data_update_end')
                ),
            ).start()

    def render(self):
        box = self.get_widget("boxWeekDays")
        remove_all_children(box)
        for day in self.week.days:
            box.add(WeekDayHandler(day).get_root_widget())

    def on_selected_date_changed(self, gobj):
        self.render()

    def on_shift_previous_week(self, ev_box, ev_btn):
        self.week.shift_prev_week()
        self.fetch_new_time_entries()

    def on_shift_next_week(self, ev_box, ev_btn):
        self.week.shift_next_week()
        self.fetch_new_time_entries()
