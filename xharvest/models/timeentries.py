from datetime import timedelta
from datetime import datetime
from operator import itemgetter
from gi.repository import GObject
from xharvest.logger import logger
from harvest.services import TimeRangeBaseService
from harvest.services import MonthTimeEntries
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

    SIGNAL_DATA_SET_CHANGED = 'data_update_end'

    __gsignals__ = {
        'time_entry_deleted': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'time_entry_saved': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'data_update_bgn': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'data_update_end': (GObject.SIGNAL_RUN_FIRST, None, ()),
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
                spent_date = time_entry['spent_date']
                spent_date = datetime.strptime(spent_date, '%Y-%m-%d').date()
                if spent_date == date_obj.date():
                    ret += time_entry['hours']
        return ret

    def fetch_data(self):
        logger.debug('TimeEntries.fetch_data bgn')
        logger.debug('TimeEntries.fetch_data emitting data_update_bgn')
        self.emit('data_update_bgn')
        self.data = WeekTimeEntriesService(
            self.oauth2,
            self.date_obj,
            ).all()['time_entries']
        logger.debug('TimeEntries.fetch_data emitting data_update_end')
        self.emit('data_update_end')
        logger.debug('TimeEntries.fetch_data end')

    def get_by_id(self, _id):
        for data in self.data:
            if int(data['id']) == int(_id):
                return data

    def save(self, time_entry_id, data):
        logger.debug('TimeEntries.save bgn')
        if time_entry_id:
            time_entry_id = int(time_entry_id)
            logger.debug(f'TimeEntries.save Updating #{time_entry_id}')
            resp = TimeEntryUpdateEndpoint(
                credential=self.oauth2,
                time_entry_id=time_entry_id,
            ).patch(data=data)
            if resp.status_code == 200:
                for e in self.data:
                    if time_entry_id == e['id']:
                        self.data.remove(e)
                self.data.append(resp.json())
                logger.debug('TimeEntries.save emitting "time_entry_saved"')
                self.emit('time_entry_saved', time_entry_id)
        else:
            resp = TimeEntryEndpoint(
                credential=self.oauth2).post(data=data)
            if resp.status_code == 201:
                self.data.append(resp.json())
                # logger.debug(f'TimeEntries.save emiting "{self.SIGNAL_DATA_SET_CHANGED}"')
                # self.emit(self.SIGNAL_DATA_SET_CHANGED)
        logger.debug('TimeEntries.save end')

    def delete(self, time_entry_id):
        logger.debug(f'TimeEntries.delete #{time_entry_id}')
        time_entry_id = int(time_entry_id)
        resp = TimeEntryUpdateEndpoint(
            credential=self.oauth2,
            time_entry_id=time_entry_id,
            ).delete()
        if resp.status_code == 200:
            idx = -1
            for e in self.data:
                if e['id'] == time_entry_id:
                    logger.debug(f'TimeEntries.delete {e["id"]} == {time_entry_id}')
                    self.data.remove(e)
                    break
            logger.debug(f'TimeEntries.delete emiting "{self.SIGNAL_DATA_SET_CHANGED}"')
            self.emit(self.SIGNAL_DATA_SET_CHANGED)