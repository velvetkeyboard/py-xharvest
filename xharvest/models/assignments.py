from datetime import datetime
from gi.repository import GObject
from harvest.services import UsersAllAssignments
from xharvest.models.base import HarvestGObject


class Assignments(HarvestGObject):

    __gsignals__ = {
        "data_update_bgn": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "data_update_end": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def sync_data(self):
        self.emit("data_update_bgn")
        self.data = UsersAllAssignments(credential=self.get_credential()).all()
        # self.log('sync_data', 'remote data', self.data)
        self.last_refresh = datetime.now()
        self.emit("data_update_end")

    def get_tasks(self, proj_id):
        for a in self.data:
            if proj_id == int(a["project"]["id"]):
                return a["task_assignments"]
