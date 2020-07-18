from gi.repository import GObject
from xharvest.logger import logger
from xharvest.auth import AuthenticationManager


class HarvestGObject(GObject.GObject):

    auth = AuthenticationManager()
    logger = logger

    def __init__(self):
        super(HarvestGObject, self).__init__()
        self.data = None

    def get_credential(self):
        return self.auth.get_credential()

    def sync_data(self):
        raise NotImplementedError

    def log(self, *args):
        pass
