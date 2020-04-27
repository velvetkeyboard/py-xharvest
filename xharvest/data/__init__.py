import pkg_resources


GLADE_FILE = pkg_resources.resource_filename(__name__, 'glade/main2.glade')
GLADE_MAIN_HEADERBAR = pkg_resources.resource_filename(__name__, 'glade/main_headerbar.glade')
GLADE_TIME_SUMMARY = pkg_resources.resource_filename(__name__, 'glade/time_summary.glade')
CSS_MAIN = pkg_resources.resource_filename(__name__, 'css/main.css')


def get_template_path(name):
    return pkg_resources.resource_filename(__name__, f'glade/{name}.glade')

def get_css_path(name):
    return pkg_resources.resource_filename(__name__, f'css/{name}.css')

def get_img_path(name):
    return pkg_resources.resource_filename(__name__, f'img/{name}')
