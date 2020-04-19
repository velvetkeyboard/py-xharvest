from gi.repository import GObject


class CustomSignals(GObject.GObject):

    __gsignals__ = {
        'selected_date_changed': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'time_entry_deleted': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'time_entry_saved': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        'time_entry_restarted': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'user_authenticated': (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
