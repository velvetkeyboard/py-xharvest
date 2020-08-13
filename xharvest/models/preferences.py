import os
import json
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


CONFIG_PATH = os.path.expanduser('~/.xharvest/config.json')


def config_changes(func):
    def wrapper(obj, *args, **kwargs):
        cfg = obj.get_config()
        ret = func(obj, cfg, *args, **kwargs)
        obj.save_config(cfg)
        return ret

    return wrapper


class Shortcuts:
    SHOW_TIME_ENTRY_FORM = 'new_time_entry'
    SHOW_TODAYS_ENTRIES = 'back_today'
    SHOW_TIME_SUMMARY = 'time_summary'


class Preferences(GObject.GObject):

    __gsignals__ = {
        "shortcuts_changed": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "show_time_summary": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    mod_maps = {
        'Control': Gdk.ModifierType.CONTROL_MASK,
        'Shift': Gdk.ModifierType.SHIFT_MASK,
    }

    def get_config(self):
        if not os.path.isfile(CONFIG_PATH):
            # TODO let's try move it out to the setup flow
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            self.save_config({
                "tray_icon": False,
                "shortcuts": {
                    Shortcuts.SHOW_TIME_ENTRY_FORM: {
                        "mod_key": "Control",
                        "key": "N",
                    },
                    Shortcuts.SHOW_TODAYS_ENTRIES: {
                        "mod_key": "Control",
                        "key": "H",
                    },
                    Shortcuts.SHOW_TIME_SUMMARY: {
                        "mod_key": "Control",
                        "key": "Y",
                    },
                },
            })
        return json.load(open(CONFIG_PATH, 'r'))

    @config_changes
    def update_shortcut_config(self, cfg, name, mod_key, key):
        cfg['shortcuts'][name] = {'mod_key': mod_key, 'key': key}

    @config_changes
    def update_minimize_to_tray_icon(self, cfg, val):
        cfg['tray_icon'] = val

    def get_minimize_to_tray_icon(self):
        return self.get_config()['tray_icon']

    def save_config(self, content):
        with open(CONFIG_PATH, 'w') as f:
            f.write(json.dumps(content, indent=2))

    def get_shortcut(self, name):
        cfg = self.get_config()
        sts = cfg['shortcuts']
        return (
            Gdk.keyval_from_name(sts[name]['key']),
            self.mod_maps[sts[name]['mod_key']],
        )

    def get_new_time_entry_accel_group(self, cb):
        '''
        Params:
            cb (function):
        '''
        key, mod_key = self.get_shortcut(Shortcuts.SHOW_TIME_ENTRY_FORM)
        accel = Gtk.AccelGroup()
        accel.connect(
                key,
                mod_key,
                0,
                cb,
                )
        return accel

    def get_back_today_accel_group(self, cb):
        '''
        Params:
            cb (function):
        '''
        key, mod_key = self.get_shortcut(Shortcuts.SHOW_TODAYS_ENTRIES)
        accel = Gtk.AccelGroup()
        accel.connect(
                key,
                mod_key,
                0,
                cb,
                )
        return accel

    def get_time_summary_accel_group(self, cb):
        '''
        Params:
            cb (function):
        '''
        key, mod_key = self.get_shortcut(Shortcuts.SHOW_TIME_SUMMARY)
        accel = Gtk.AccelGroup()
        accel.connect(key, mod_key, 0, cb)
        return accel

    def get_accel_group(self, shortcut_name, cb):
        '''
        Params:
            shortcut_name (str):
            cb (function):
        '''
        key, mod_key = self.get_shortcut(shortcut_name)
        accel = Gtk.AccelGroup()
        accel.connect(key, mod_key, 0, cb)
        return accel
