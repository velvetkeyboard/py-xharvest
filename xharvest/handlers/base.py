import re
from xharvest.data import get_template_path
from xharvest.models import TimeEntries
from xharvest.models import Week
from xharvest.models import User
from xharvest.models import Assignments
from xharvest.models import AuthenticationFlow
from xharvest.models import Preferences
from xharvest.auth import AuthenticationManager
from gi.repository import Gtk


class Handler(object):
    template = ""
    widgets = []
    root_widget = "root"
    re_pattern = re.compile(r"(?<!^)(?=[A-Z])")
    auth_flow = AuthenticationFlow()
    user = User()
    assignments = Assignments()
    time_entries = TimeEntries()
    week = Week()
    preferences = Preferences()

    def __init__(self, builder=None):
        self.builder = builder or Gtk.Builder()
        if self.widgets:
            self.builder.add_objects_from_file(
                self.get_template(), self.widgets)
        else:
            self.builder.add_from_file(self.get_template())
        self.builder.connect_signals(self)
        self.bind_signals()
        self.bind_data()
        # self.builder.get_object(self.root_widget).show_all()
        # self.get_root_widget().show_all()

    def is_user_authenticated(self):
        return AuthenticationManager().is_user_authenticated()

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
