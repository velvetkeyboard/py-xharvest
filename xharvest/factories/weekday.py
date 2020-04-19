from xharvest.factories.base import Factory


class WeekDayFactory(Factory):
    widget_ids = ('eventBoxWeekDay',)
    root_widget_name = 'eventBoxWeekDay'

    def bind(self):
        self.builder.get_object('eventBoxWeekDay')\
                    .set_name(f'{self.data.get_isoformat()}')
        if self.data.is_selected:
            self.builder.get_object('labelWeekDayName')\
                       .set_markup(f'<b>{self.data.name}</b>')
            self.builder.get_object('labelWeekDayDate')\
                        .set_markup(f'<b>{self.data}</b>')
        else:
            self.builder.get_object('labelWeekDayName')\
                        .set_markup(f'{self.data.name}')
            self.builder.get_object('labelWeekDayDate')\
                        .set_markup(f'{self.data}')

