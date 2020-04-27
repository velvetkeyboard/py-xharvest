from xharvest.handlers.base import Handler


class WeekDayHandler(Handler):

    template = "weekday"
    root_widget = "eb_weekday"

    def __init__(self, weekday):
        self.weekday = weekday
        super(WeekDayHandler, self).__init__()

    def bind_data(self):
        self.lbl_name = self.builder.get_object("labelWeekDayName")
        self.lbl_date = self.builder.get_object("labelWeekDayDate")
        self.render()

    def bind_signals(self):
        self.week.connect(
            "selected_date_changed", self.on_selected_date_changed)
        self.time_entries.connect(
            "data_update_end", self.on_time_entries_data_was_updated
        )

    def get_weekday_name(self):
        return self.weekday.date_obj.strftime("%a")

    def get_weekday_date(self):
        # return self.weekday.date_obj.strftime('%m/%d')
        ret = self.time_entries.get_total_hours_by_day(self.weekday.date_obj)
        return f"{ret:02.02f}"

    def set_bold(self):
        self.lbl_name.set_markup(f"<b>{self.get_weekday_name()}</b>")
        self.lbl_date.set_markup(f"<b>{self.get_weekday_date()}</b>")

    def set_regular(self):
        self.lbl_name.set_markup(f"{self.get_weekday_name()}")
        self.lbl_date.set_markup(f"{self.get_weekday_date()}")

    def render(self):
        date_obj = self.week.get_selected_date().date()
        if self.weekday.date_obj.date() != date_obj:
            self.set_regular()
        else:
            self.set_bold()

    def on_selected_date_changed(self, gobj):
        self.render()

    def on_time_entries_data_was_updated(self, gobj):
        self.render()

    def on_eb_weekday_button_press_event(self, ev_box, ev_btn):
        self.week.set_selected_date(self.weekday.date_obj)
        self.week.emit("selected_date_changed")
