from gi.repository import GObject
# from xharvest.auth import AuthenticationManager


class AuthenticationFlow(GObject.GObject):

    __gsignals__ = {
        "user_authenticated": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "user_signout": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
