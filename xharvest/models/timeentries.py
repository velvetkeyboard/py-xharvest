from datetime import timedelta
from gi.repository import GObject
from harvest.services import TimeRangeBaseService
from harvest.endpoints import TimeEntryUpdateEndpoint
from harvest.endpoints import TimeEntryEndpoint


class WeekTimeEntriesService(TimeRangeBaseService):
    def __init__(self, credential, date):
        '''
        Params:
            credential (harvest.credentials.OAuth2Credential):
            date (datetime.datetime):
        '''
        self.date = date
        super(WeekTimeEntriesService, self).__init__(credential)

    def get_date_range(self):
        start = self.date + timedelta(0 - self.date.weekday())
        end = self.date + timedelta(6 - self.date.weekday())
        ret = (
            start.date(),
            end.date(),
        )
        return ret


class TimeEntries(GObject.GObject):

    __gsignals__ = {
        'time_entry_deleted': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'time_entry_saved': (GObject.SIGNAL_RUN_FIRST, None, (str,))
    }

    def __init__(self, oauth2=None, date_obj=None, data=None):
        super(TimeEntries, self).__init__()
        self.data = data
        self.oauth2 = oauth2
        self.date_obj = date_obj

    def fetch_data(self):
        self.data = WeekTimeEntriesService(
            self.oauth2,
            self.date_obj,
            ).all()['time_entries']

    def get_by_id(self, _id):
        for data in self.data:
            if int(data['id']) == int(_id):
                return data

    def save(self, time_entry_id, data):
        if time_entry_id:
            time_entry_id = int(time_entry_id)
            resp = TimeEntryUpdateEndpoint(
                credential=self.oauth2,
                time_entry_id=time_entry_id,
            ).patch(data=data)
            if resp.status_code == 200:
                for e in self.data:
                    if time_entry_id == e['id']:
                        self.data.remove(e)
                self.data.append(resp.json())
        else:
            resp = TimeEntryEndpoint(
                credential=self.oauth2).post(data=data)
            if resp.status_code == 201:
                self.data.append(resp.json())

    def delete(self, time_entry_id):
        time_entry_id = int(time_entry_id)
        resp = TimeEntryUpdateEndpoint(
            credential=self.oauth2,
            time_entry_id=time_entry_id,
            ).delete()
        idx = -1
        for e in self.data:
            if e['id'] == time_entry_id:
                self.data.remove(e)
                break
