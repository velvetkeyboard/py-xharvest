import pkg_resources


def get_template_path(name):
    return pkg_resources.resource_filename(__name__, f"glade/{name}.glade")


def get_css_path(name):
    return pkg_resources.resource_filename(__name__, f"css/{name}.css")


def get_img_path(name):
    return pkg_resources.resource_filename(__name__, f"img/{name}")


def get_app_icon_path():
    return get_img_path('xharvest.png')
