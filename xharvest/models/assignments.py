from datetime import datetime
from harvest.services import UsersAllAssignments


class Assignments():

    def __init__(self):
        self.data = None
        self.oauth2 = None
        self.last_refresh = None

    def fetch_data(self):
        self.data = UsersAllAssignments(credential=self.oauth2).all()
        self.last_refresh = datetime.now()

    def get_tasks(self, proj_id):
        for a in self.data:
            if proj_id == int(a['project']['id']):
                return a['task_assignments']

