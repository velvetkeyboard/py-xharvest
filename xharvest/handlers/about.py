from datetime import datetime
from xharvest import __version__
from xharvest import __author__
from xharvest import __author_email__
from xharvest import __license__
from xharvest import __app_name__
from xharvest.utils import get_gravatar_img_as_pixbuf
from xharvest.logger import logger
from xharvest.data import get_img_path
from xharvest.handlers.base import Handler


class AboutHandler(Handler):

    def bind_data(self):
        # ---------------------------------------------------[Logo and Version]
        logger.debug(get_img_path("xharvest.png"))
        self.builder.get_object("label_app_logo").set_from_file(
            get_img_path("xharvest.png")
        )
        self.builder.get_object("label_app_version")\
            .set_markup(f"v{__version__}")
        # -------------------------------------------[License and Registration]
        year_now = datetime.now().strftime("%Y")
        self.builder.get_object("label_app_license").set_markup(
            f"License - {__license__}"
        )
        self.builder.get_object("label_app_year").set_markup(
            f"🄯 2020 - {year_now} {__app_name__}"
        )
        # ----------------------------------------------------[Author Section]
        self.builder.get_object("label_app_author_name")\
            .set_markup(f"{__author__}")
        self.builder.get_object("label_app_author_email")\
            .set_markup(f"{__author_email__}")
        self.builder.get_object("img_app_author_avatar")\
            .set_from_pixbuf(get_gravatar_img_as_pixbuf(__author_email__))
