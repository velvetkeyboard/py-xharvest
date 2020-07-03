from datetime import datetime
from harvest.services import UsersAllAssignments
from gi.repository import GObject


class Assignments(GObject.GObject):

    __gsignals__ = {
        "data_update_bgn": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "data_update_end": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        super(Assignments, self).__init__()
        self.data = None
        self.cred = None
        self.last_refresh = None

    def fetch_data(self):
        self.emit("data_update_bgn")
        self.data = UsersAllAssignments(credential=self.cred).all()
        self.last_refresh = datetime.now()
        self.emit("data_update_end")

    def get_tasks(self, proj_id):
        for a in self.data:
            if proj_id == int(a["project"]["id"]):
                return a["task_assignments"]
