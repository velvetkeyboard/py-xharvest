import calendar


class WeekDay(object):
    def __init__(self, date_obj, selected=False):
        self.date_obj = date_obj
        self.is_selected = selected
        self.name = calendar.day_name[self.date_obj.weekday()][:3]

    def get_isoformat(self):
        return self.date_obj.date().isoformat()

    def __str__(self):
        return f"{self.date_obj.day:02d}/{self.date_obj.month:02d}"

    def __repr__(self):
        return self.__str__()
