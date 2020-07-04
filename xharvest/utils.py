import urllib
import hashlib
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf


def find_child_by_name(widget, name):
    if widget.get_name() == name:
        return widget
    if hasattr(widget, "get_children"):
        for w in widget.get_children():
            ret = find_child_by_name(w, name)
            if ret:
                return ret


def remove_all_children(widget):
    for c in widget.get_children():
        widget.remove(c)


def get_gravatar_img_as_pixbuf(email):
    size = 40
    h = hashlib.md5(email.lower().encode("utf-8")).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d={size}"
    response = urllib.request.urlopen(url)
    input_stream = Gio.MemoryInputStream.new_from_data(
        response.read(), None)
    pixbuf = Pixbuf.new_from_stream(input_stream, None)
    return pixbuf
