from threading import Thread
from gi.repository import GLib


def gtk_thread_cb(func):
    def wrapper(thread=None, *args, **kwargs):
        if thread:
            if thread.is_alive():
                return True
            thread.join()
        return func(thread, *args, **kwargs)

    return wrapper


def gtk_thread_method_cb(func):
    def wrapper(obj, thread=None, *args, **kwargs):
        if thread:
            if thread.is_alive():
                return True
            thread.join()
        return func(obj, thread, *args, **kwargs)

    return wrapper


class GtkThread(Thread):
    def __init__(self, *args, **kwargs):
        self.target_cb = None
        self.target_cb_args = []

        if "target_cb" in kwargs.keys():
            self.target_cb = kwargs.pop("target_cb")
        if "target_cb_args" in kwargs.keys():
            self.target_cb_args = kwargs.pop("target_cb_args", [])

        super(GtkThread, self).__init__(*args, **kwargs)

    def start(self):
        self.daemon = True
        super(GtkThread, self).start()
        if self.target_cb:
            args = [self] + list(self.target_cb_args)
            GLib.idle_add(self.target_cb, *args)
