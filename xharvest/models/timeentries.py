from datetime import datetime
from gi.repository import GObject
from harvest.services import WeekTimeEntriesService
from harvest.endpoints import TimeEntryUpdateEndpoint
from harvest.endpoints import TimeEntryEndpoint
from xharvest.models.base import HarvestGObject


class TimeEntries(HarvestGObject):

    SIGNAL_DATA_SET_CHANGED = "data_update_end"

    __gsignals__ = {
        "time_entry_deleted": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "time_entry_saved": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "data_update_bgn": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "data_update_end": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "time_entry_restarted": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "time_entries_were_rendered": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self, cred=None, date_obj=None, data=None):
        super(TimeEntries, self).__init__()
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

    def sync_data(self):
        self.data = WeekTimeEntriesService(
            self.get_credential(), self.date_obj,).all()["time_entries"]

    def get_by_id(self, uid):
        for data in self.data:
            if int(data["id"]) == int(uid):
                return data

    def save(self, time_entry_id, data):
        if time_entry_id:
            time_entry_id = int(time_entry_id)
            resp = TimeEntryUpdateEndpoint(
                credential=self.get_credential(), time_entry_id=time_entry_id,
            ).patch(data=data)
            if resp.status_code == 200:
                for e in self.data:
                    if time_entry_id == e["id"]:
                        self.data.remove(e)
                        break
                self.data.append(resp.json())
        else:
            resp = TimeEntryEndpoint(
                credential=self.get_credential()).post(data=data)
            if resp.status_code == 201:
                self.data.append(resp.json())
                time_entry_id = resp.json()['id']
        return time_entry_id

    def delete(self, time_entry_id):
        time_entry_id = int(time_entry_id)
        resp = TimeEntryUpdateEndpoint(
            credential=self.get_credential(), time_entry_id=time_entry_id,
        ).delete()
        if resp.status_code == 200:
            # idx = -1
            for e in self.data:
                if e["id"] == time_entry_id:
                    self.data.remove(e)
                    break
            # self.emit(self.SIGNAL_DATA_SET_CHANGED)
