from datetime import datetime
from xharvest.handlers.base import Handler


class WeekDayHandler(Handler):

    LABEL_WEEKDAYNAME = 'labelWeekDayName'
    LABEL_WEEKDAYDATE = 'labelWeekDayDate'

    def set_label_bold(self, w):
        w.set_markup(f'<b>{w.get_label()}</b>')

    def set_label_regular(self, w):
        tmp = w.get_label().replace('<b>', '').replace('</b>', '')
        w.set_markup(f'{tmp}')

    def on_select_week_day(self, event_box, event_button):
        lbl_name = self.find_child_by_name(event_box, self.LABEL_WEEKDAYNAME)
        lbl_date = self.find_child_by_name(event_box, self.LABEL_WEEKDAYDATE)
        self.set_label_bold(lbl_name)
        self.set_label_bold(lbl_date)
        box = event_box.get_parent()
        for w in box.get_children():
            if id(w) != id(event_box):
                self.set_label_regular(
                    self.find_child_by_name(w, self.LABEL_WEEKDAYNAME))
                self.set_label_regular(
                    self.find_child_by_name(w, self.LABEL_WEEKDAYDATE))
        iso_date = event_box.get_name()
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        self.week.set_selected_date(date_obj)
        self.week.emit('selected_date_changed', iso_date)

