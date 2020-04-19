from xharvest.models import TimeEntries
from xharvest.models import Assignments
from xharvest.models import OAuth2CredentialManager
from xharvest.models import User
from xharvest.models import Week
from xharvest.models import CustomSignals


class Handler(object):
    time_entries = TimeEntries()
    assignments = Assignments()
    week = Week()
    oauth2_mng = OAuth2CredentialManager()
    user = User()
    custom_signals = CustomSignals()

    def __init__(self, builder=None):
        self.builder = builder

    def set_builder(self, builder):
        self.builder = builder

    def find_child_by_name(self, widget, name):
        widget_name = widget.get_name()
        if widget_name == name:
            return widget
        if hasattr(widget, 'get_children') and widget.get_children():
            for w in widget.get_children():
                ret = self.find_child_by_name(w, name)
                if ret:
                    return ret

    def remove_all_children(self, widget):
        for c in widget.get_children():
            widget.remove(c)

