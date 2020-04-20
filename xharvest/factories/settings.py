from xharvest.factories.base import Factory
from xharvest.models import Author


class SettingsFactory(Factory):
    widget_ids = ('appWindowSettings',)
    root_widget_name = 'appWindowSettings'

    bind_list = [
        ('labelUser')
    ]

    def bind(self):
        self.handler.win = self.builder.get_object('appWindowSettings')
        self.builder.get_object('labelUserFirstName')\
                    .set_label(self.handler.user.data['first_name'])
        self.builder.get_object('labelUserLastName')\
                    .set_label(self.handler.user.data['last_name'])
        self.builder.get_object('labelUserEmail')\
                    .set_label(self.handler.user.data['email'])
        self.builder.get_object('checkButtonUserIsContractor')\
                    .set_active(self.handler.user.data['is_contractor'])
        self.builder.get_object('checkButtonUserIsAdmin')\
                    .set_active(self.handler.user.data['is_admin'])
        self.builder.get_object('checkButtonUserIsProjManager')\
                    .set_active(self.handler.user.data['is_project_manager'])
        self.builder.get_object('labelUserLastName')\
                    .set_label(self.handler.user.data['last_name'])
        self.builder.get_object('imageUserAvatar').set_from_pixbuf(
                                self.handler.user.get_avatar_img_as_pixbuf())
        self.builder.get_object('imageAuthorAvatar')\
                    .set_from_pixbuf(Author().get_avatar_img_as_pixbuf())

