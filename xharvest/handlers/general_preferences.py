from xharvest.handlers.base import Handler


class GeneralPreferencesHandler(Handler):

    def bind_data(self):
        self.cbtn_close_to_notification_icon = self.get_widget(
                'cbtn_close_to_notification_icon')
        self.cbtn_detect_idle_time = self.get_widget(
                'cbtn_detect_idle_time')
        self.entrybuffer_idle_min = self.get_widget(
                'entrybuffer_idle_min')

        self.cbtn_close_to_notification_icon.set_active(
                self.preferences.get_minimize_to_tray_icon(),
                )
        self.cbtn_detect_idle_time.set_active(
                self.preferences.get_detect_idle_time(),
                )
        self.entrybuffer_idle_min.set_text(
                str(int(self.preferences.get_idle_sec() / 60)),
                -1)

    def on_close_to_notification(self, cbtn):
        self.preferences.update_minimize_to_tray_icon(cbtn.get_active())

    def on_detect_idle_time_toggled(self, cbtn):
        self.preferences.update_detect_idle_time(cbtn.get_active())

    def on_entrybuffer_idle_min_changed(self, entry_b, *args):
        val = entry_b.get_text()
        if val:  # insert mode
            val = int(val) * 60
            self.preferences.update_idle_sec(val)

