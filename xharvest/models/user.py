import urllib.parse
from gi.repository import GObject
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf
from harvest.services import CurrentUser


class User(GObject.GObject):

    def __init__(self, oauth2=None, data=None):
        super(User, self).__init__()
        self.data = data
        self.oauth2 = oauth2

    def fetch_data(self):
        self.data = CurrentUser(self.oauth2).get()

    def get_avatar_img_as_pixbuf(self):
        url = self.data['avatar_url']
        response = urllib.request.urlopen(url)
        input_stream = Gio.MemoryInputStream.new_from_data(
                response.read(), None) 
        pixbuf = Pixbuf.new_from_stream(input_stream, None)
        return pixbuf
