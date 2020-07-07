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
        self.data = UsersAllAssignments(credential=self.get_credential()).all()
        self.last_refresh = datetime.now()

    def get_tasks(self, proj_id):
        for a in self.data:
            if proj_id == int(a["project"]["id"]):
                return a["task_assignments"]
