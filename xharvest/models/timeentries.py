from datetime import timedelta
from datetime import datetime
from gi.repository import GObject
from xharvest.logger import logger
from harvest.services import TimeRangeBaseService
from harvest.services import WeekTimeEntriesService
from harvest.endpoints import TimeEntryUpdateEndpoint
from harvest.endpoints import TimeEntryEndpoint


class TimeEntries(GObject.GObject):

    SIGNAL_DATA_SET_CHANGED = "data_update_end"

    __gsignals__ = {
        "time_entry_deleted": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "time_entry_saved": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "data_update_bgn": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "data_update_end": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "time_entry_restarted": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "time_entries_were_rendered": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, oauth2=None, date_obj=None, data=None):
        super(TimeEntries, self).__init__()
        self.data = data or []
        self.oauth2 = oauth2
        self.date_obj = date_obj or datetime.now()

    def get_total_hours_by_day(self, date_obj):
        ret = 0.0
        if self.data:
            for time_entry in self.data:
                spent_date = time_entry["spent_date"]
                spent_date = datetime.strptime(spent_date, "%Y-%m-%d").date()
                if spent_date == date_obj.date():
                    ret += time_entry["hours"]
        return ret

    def fetch_data(self):
        self.emit("data_update_bgn")
        self.data = WeekTimeEntriesService(self.oauth2, self.date_obj,).all()[
            "time_entries"
        ]
        logger.debug("TimeEntries.fetch_data emitting data_update_end")
        self.emit("data_update_end")

    def get_by_id(self, _id):
        for data in self.data:
            if int(data["id"]) == int(_id):
                return data

    def save(self, time_entry_id, data):
        if time_entry_id:
            time_entry_id = int(time_entry_id)
            resp = TimeEntryUpdateEndpoint(
                credential=self.oauth2, time_entry_id=time_entry_id,
            ).patch(data=data)
            if resp.status_code == 200:
                for e in self.data:
                    if time_entry_id == e["id"]:
                        self.data.remove(e)
                self.data.append(resp.json())
                logger.debug('TimeEntries.save emitting "time_entry_saved"')
                self.emit("time_entry_saved", time_entry_id)
        else:
            resp = TimeEntryEndpoint(credential=self.oauth2).post(data=data)
            if resp.status_code == 201:
                self.data.append(resp.json())

    def delete(self, time_entry_id):
        time_entry_id = int(time_entry_id)
        resp = TimeEntryUpdateEndpoint(
            credential=self.oauth2, time_entry_id=time_entry_id,
        ).delete()
        if resp.status_code == 200:
            # idx = -1
            for e in self.data:
                if e["id"] == time_entry_id:
                    self.data.remove(e)
                    break
            # self.emit(self.SIGNAL_DATA_SET_CHANGED)
