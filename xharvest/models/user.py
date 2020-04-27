import os.path
import urllib.parse
from gi.repository import GObject
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf
from harvest.services import CurrentUser
from xharvest.logger import logger


class User(GObject.GObject):

    USER_AVATAR_SIZE = 48

    def __init__(self, oauth2=None, data=None):
        super(User, self).__init__()
        self.data = data
        self.oauth2 = oauth2

    def fetch_data(self):
        self.data = CurrentUser(self.oauth2).get()

    def get_avatar_img_file_path(self):
        file_path = os.path.expanduser("~/.xharvest/user_avatar.jpg")
        logger.debug(f"User.get_avatar_img_file_path returning {file_path}")
        return file_path

    def download_user_avatar(self):
        file_path = self.get_avatar_img_file_path()
        url = self.data["avatar_url"]
        resp = urllib.request.urlopen(url)
        with open(file_path, "wb") as f:
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
