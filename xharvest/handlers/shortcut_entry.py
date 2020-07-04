from gi.repository import Gdk
from xharvest.handlers.base import Handler


class ShortcutEntryHandler(Handler):

    def __init__(self, name, bind):
        self.shortcut_name = name
        self.shortcut_bind = bind
        self.flag = False
        self.new_mod_key = None
        self.new_key = None
        super(ShortcutEntryHandler, self).__init__()

    def bind_data(self):
        self.label_shortcut_name = self.get_widget('label_shortcut_name')
        # self.label_shortcut_keybind = self.get_widget(
        # 'label_shortcut_keybind')
        self.btn_shortcut_remap = self.get_widget('btn_shortcut_remap')

        self.label_shortcut_name.set_label(self.shortcut_name)
        self.btn_shortcut_remap.set_label(
                f'{self.shortcut_bind["mod_key"]} + \
                {self.shortcut_bind["key"]}')

    def on_remapping(self, btn):
        if not self.flag:
            self.flag = True
            self.btn_shortcut_remap.set_label('...')

    def on_root_key_press_event(self, gtk_box, gdk_eventkey):
        if self.flag:
            keyname = Gdk.keyval_name(gdk_eventkey.keyval)
            keyname = keyname.split('_')[0]
            if not self.new_mod_key:
                self.new_mod_key = keyname
            elif not self.new_key:
                self.new_key = keyname
                self.flag = False
                self.shortcut_bind['mod_key'] = self.new_mod_key
                self.shortcut_bind['key'] = self.new_key.upper()
                self.preferences.update_shortcut_config(
                        self.shortcut_name,
                        self.shortcut_bind['mod_key'],
                        self.shortcut_bind['key'],
                    )
                self.new_mod_key = None
                self.new_key = None
                self.btn_shortcut_remap.set_label(
                    f'{self.shortcut_bind["mod_key"]} + \
                    {self.shortcut_bind["key"]}')
