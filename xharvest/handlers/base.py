import re
from xharvest.data import get_template_path
# from xharvest.models import CustomSignals as GlobalSignals
from xharvest.models import TimeEntries
from xharvest.models import Week
from xharvest.models import User
from xharvest.models import Assignments
from xharvest.models import OAuth2CredentialManager
from gi.repository import Gtk


class Handler(object):
    template = ""
    widgets = []
    root_widget = "root"
    # global_signals = GlobalSignals()
    oauth2 = OAuth2CredentialManager()
    user = User()
    time_entries = TimeEntries()
    week = Week()
    assignments = Assignments()
    re_pattern = re.compile(r"(?<!^)(?=[A-Z])")

    def __init__(self, builder=None):
        self.builder = builder or Gtk.Builder()
        if self.widgets:
            self.builder.add_objects_from_file(
                self.get_template(), self.widgets)
        else:
            self.builder.add_from_file(self.get_template())
        self.builder.connect_signals(self)
        self.initialize_gobjects()
        self.bind_signals()
        self.bind_data()
        # self.builder.get_object(self.root_widget).show_all()
        # self.get_root_widget().show_all()

    def initialize_gobjects(self):
        if not self.user.oauth2:
            self.user.oauth2 = self.oauth2.get_credential()
        if not self.assignments.oauth2:
            self.assignments.oauth2 = self.oauth2.get_credential()
        if not self.time_entries.oauth2:
            self.time_entries.oauth2 = self.oauth2.get_credential()

    def bind_signals(self):
        pass

    def bind_data(self):
        pass

    def set_builder(self, builder):
        self.builder = builder

    def get_builder(self):
        return self.builder

    def set_template(self, name):
        self.template = name

    def get_template(self):
        if self.template:
            return get_template_path(self.template)
        else:
            name = (
                self.re_pattern.sub("_", self.__class__.__name__)
                .lower()
                .replace("_handler", "")
            )
        return get_template_path(self.template or name)

    def get_widget(self, w_id):
        return self.get_builder().get_object(w_id)

    def get_root_widget(self):
        ret = self.get_widget(self.root_widget)
        return ret
