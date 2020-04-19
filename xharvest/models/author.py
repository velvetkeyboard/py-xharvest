import urllib
import hashlib
from gi.repository import Gio
from gi.repository.GdkPixbuf import Pixbuf


class Author(object):

    def get_avatar_img_as_pixbuf(self):
        email = 'ramon@vyscond.io'
        size = 40
        h = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
        url = f'https://www.gravatar.com/avatar/{h}?d={size}'
        response = urllib.request.urlopen(url)
        input_stream = Gio.MemoryInputStream.new_from_data(
                response.read(), None) 
        pixbuf = Pixbuf.new_from_stream(input_stream, None)
        return pixbuf
