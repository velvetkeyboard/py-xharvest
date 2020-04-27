from datetime import timedelta
from datetime import datetime
from operator import itemgetter
from gi.repository import GObject
from xharvest.logger import logger
from harvest.services import TimeRangeBaseService
from harvest.services import MonthTimeEntries
from harvest.endpoints import TimeEntryUpdateEndpoint
from harvest.endpoints import TimeEntryEndpoint



class TimeSummary(GObject.GObject):

    __gsignals__ = {
        'data_update_bgn': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'data_update_end': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, oauth2=None, data=None):
        super(TimeSummary, self).__init__()
        self.data = data or []
        self.oauth2 = oauth2
        self.today = 0.0
        self.yesterday = 0.0 
        self.week = 0.0
        self.month = 0.0

    def fetch_data(self, date_obj):
        svc = MonthTimeEntries(self.oauth2)
        svc.set_month(date_obj.year, date_obj.month)
        self.data = svc.all()['time_entries']
        self.gen_summary(date_obj)

    def gen_summary(self, date_obj):
        self.today = 0.0
        self.yesterday = 0.0 
        self.week = 0.0
        self.month = 0.0
        week_bgn = (date_obj + timedelta(0 - date_obj.weekday())).date()
        week_end = (date_obj + timedelta(6 - date_obj.weekday())).date()
        if self.data:
            for time_entry in self.data:
                spent_date = time_entry['spent_date']
                spent_date = datetime.strptime(spent_date, '%Y-%m-%d').date()
                if spent_date == date_obj.date():
                    self.today += time_entry['hours']
                elif spent_date == date_obj.date() - timedelta(days=1):
                    self.yesterday += time_entry['hours']
                elif spent_date >= week_bgn and spent_date <= week_end:
                    self.week += time_entry['hours']
                self.month += time_entry['hours']