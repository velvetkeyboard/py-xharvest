from decimal import Decimal


class Hour(object):

    HARVEST_SEC = (Decimal(1) / Decimal(60)) / Decimal(60)

    def __init__(self, value):
        if "." in str(value):
            value = ((Decimal(value) * 100) / self.HARVEST_SEC) / 100
        elif ":" in str(value):
            hours, mins = value.split(":")
            value = (3600 * hours) + (60 * mins)
        # Total in secs
        self.value = int(value)

    def add_sec(self, increment=1):
        self.value += increment

    def add_min(self):
        self.value += 3600

    def as_harvest(self):
        return self.HARVEST_SEC * Decimal(self.value)

    def as_harvest_str(self):
        return f"{self.as_harvest():.2f}"

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value
