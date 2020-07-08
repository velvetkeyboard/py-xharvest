from datetime import timedelta
from datetime import datetime
from gi.repository import GObject
from harvest.services import MonthTimeEntries
from xharvest.models.base import HarvestGObject


class TimeSummary(HarvestGObject):

    __gsignals__ = {
        "data_update_bgn": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "data_update_end": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, cred=None, data=None):
        super(TimeSummary, self).__init__()
        self.data = data or []
        self.today = 0.0
        self.yesterday = 0.0
        self.week = 0.0
        self.month = 0.0

    def sync_data(self, date_obj):
        svc = MonthTimeEntries(self.get_credential())
        svc.set_month(date_obj.year, date_obj.month)
        self.data = svc.all()["time_entries"]
        self.gen_summary(date_obj)

    def gen_summary(self, date_obj):
        self.today = 0.0
        self.yesterday = 0.0
        self.week = 0.0
        self.month = 0.0
        week_bgn = (date_obj + timedelta(0 - date_obj.weekday())).date()
        week_end = (date_obj + timedelta(5 - date_obj.weekday())).date()
        if self.data:
            for time_entry in self.data:
                spent_date = time_entry["spent_date"]
                spent_date = datetime.strptime(spent_date, "%Y-%m-%d").date()
                if spent_date == date_obj.date():
                    self.today += time_entry["hours"]
                elif spent_date == date_obj.date() - timedelta(days=1):
                    self.yesterday += time_entry["hours"]
                if spent_date >= week_bgn and spent_date <= week_end:
                    self.week += time_entry["hours"]
                self.month += time_entry["hours"]
