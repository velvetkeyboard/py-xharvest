from xharvest.factories.base import Factory


class TimeEntryFactory(Factory):
    widget_ids = ('boxTimeEntry',)
    root_widget_name = 'boxTimeEntry'

    def bind(self):
        proj_label = f'{self.data["project"]["name"]}'
        if self.data['project']['code']:
            proj_label = f'<b>[{self.data["project"]["code"]}] {proj_label}</b>'

        self.builder.get_object('labelTimeEntryNotes')\
                    .set_markup(f'<i>{self.data["notes"]}</i>')
        self.builder.get_object('labelTimeEntryProject')\
                    .set_markup(proj_label)
        self.builder.get_object('labelTimeEntryTask')\
                    .set_markup(f"<b>{self.data['task']['name']}</b>")
        self.builder.get_object('labelTimeEntryHours')\
                    .set_markup(f"<b>{self.data['hours']:02.02f}</b>")
        self.builder.get_object('eventBoxTimeEntryEdit')\
                    .set_name(str(self.data['id']))

        self.handler.spinner = self.builder.get_object('spinnerTimeEntry')
        self.handler.eb_toggle = self.builder.get_object(
                'eventBoxTimeEntryToggleRunning')
        self.handler.img_toggle = self.builder.get_object(
                'imageTimeEntryToggleRunning')
        self.handler.label_hours = self.builder.get_object(
                'labelTimeEntryHours')

        if self.data['is_running']:
            self.handler.start_chronometer_cb()
