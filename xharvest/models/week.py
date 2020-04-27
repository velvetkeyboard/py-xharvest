from datetime import timedelta
from datetime import datetime
from gi.repository import GObject
from xharvest.models.weekday import WeekDay


class Week(GObject.GObject):

    __gsignals__ = {
        "selected_date_changed": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "set_selected_date_today": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        super(Week, self).__init__()
        self.selected_date = datetime.now()
        self.days = []

    def get_selected_date(self):
        return self.selected_date

    def set_selected_date(self, date_obj):
        self.selected_date = date_obj
        self.gen_days()

    def gen_days(self):
        start = 0 - self.selected_date.date().weekday()
        end = 7 - self.selected_date.date().weekday()
        self.days = []
        for i in range(start, end):
            wdate = self.selected_date + timedelta(days=i)
            day = WeekDay(wdate, self.selected_date == wdate)
            self.days.append(day)

    def shift_prev_week(self):
        self.selected_date = self.selected_date - timedelta(
            days=self.selected_date.weekday() + 1
        )
        self.gen_days()

    def shift_next_week(self):
        self.selected_date = self.selected_date + timedelta(
            days=7 - self.selected_date.weekday()
        )
        self.gen_days()

    def __str__(self):
        return f'<Week@{id(self)} "{self.selected_date}" {self.days}>'
