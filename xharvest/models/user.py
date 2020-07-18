import os.path
import urllib.parse
from gi.repository import GObject
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf
from harvest.services import CurrentUser
from xharvest.data import get_img_path
from xharvest.models.base import HarvestGObject


class User(HarvestGObject):

    USER_AVATAR_PATH = "~/.xharvest/user_avatar.jpg"
    USER_AVATAR_PLACEHOLDER = get_img_path("rubberduck.jpg")

    USER_AVATAR_SIZE = 48

    __gsignals__ = {
        "avatar_download_bgn": (GObject.SIGNAL_RUN_FIRST, None, ()),
        "avatar_download_end": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def sync_data(self):
        self.data = CurrentUser(self.get_credential()).get()

    def get_avatar_img_file_path(self):
        file_path = os.path.expanduser(self.USER_AVATAR_PATH)
        if not os.path.isfile(file_path):
            file_path = os.path.expanduser(self.USER_AVATAR_PLACEHOLDER)
        return file_path

    def download_user_avatar(self):
        file_path = os.path.expanduser(self.USER_AVATAR_PATH)
        if not os.path.isfile(file_path):
            url = self.data["avatar_url"]
            resp = urllib.request.urlopen(url)
            with open(file_path, "xb") as f:
                f.write(resp.read())

    def get_avatar_img_as_pixbuf(self, mode="file"):
        if mode == "stream":
            url = self.data["avatar_url"]
            response = urllib.request.urlopen(url)
            input_stream = Gio.MemoryInputStream.new_from_data(
                response.read(), None)
            pixbuf = Pixbuf.new_from_stream(input_stream, None)
        elif mode == "file":
            pixbuf = Pixbuf.new_from_file_at_size(
                self.get_avatar_img_file_path(),
                self.USER_AVATAR_SIZE,
                self.USER_AVATAR_SIZE,
            )
        return pixbuf

    def get_full_name(self):
        return f"{self.data['first_name']} {self.data['last_name']}"
