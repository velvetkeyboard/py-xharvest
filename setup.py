import os.path
from setuptools import setup, find_packages
from xharvest import __version__
from xharvest import __app_name__
from xharvest import __author__
from xharvest import __author_email__
from xharvest import __license__


# -----------------------------------------------------------------------[Meta]

with open('README.md', 'r') as f:
    long_description = f.read()

# ---------------------------------------------------------------------[Assets]

HOME_DIR = os.path.expanduser('~')
DATA_PATH = f"{HOME_DIR}/.local/share"
XHARVEST_CFG_PATH = f"{HOME_DIR}/.xharvest"

data_files = [
    (
        f'{XHARVEST_CFG_PATH}',
        ['data/rubberduck.jpg'],
    ),
    (
        f'{DATA_PATH}/applications',
        ['data/org.velvetkeyboad.xHarvest.desktop']),
    (
        f'{DATA_PATH}/icons/hicolor/128x128/apps/',
        ['data/hicolor/128x128/xharvest.png']
    ),
    (
        f'{DATA_PATH}/icons/hicolor/48x48/apps/',
        ['data/hicolor/48x48/xharvest.png']
    ),
    (
        f'{DATA_PATH}/icons/hicolor/32x32/apps/',
        ['data/hicolor/32x32/xharvest.png']
    ),
    (
        f'{DATA_PATH}/icons/hicolor/16x16/apps/',
        ['data/hicolor/16x16/xharvest.png']
    ),
]

setup(
    name=__app_name__,
    version=__version__,
    url='https://github.com/velvetkeyboad/py-xharvest',
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    description='Unofficial Harvest desktop for Linux',
    long_description=long_description,
    install_requires=[
        'pycairo==1.19.1',
        'PyGObject==3.34.0',
        'keyring==21.2.0',
        'harvest-api==0.2.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    extras_require={
        'flatpak': [
            'keyrings.cryptfile==1.3.4'
        ]
    },
    package_data={
        '': [
            'data/glade/*.glade',
            'data/css/*.css',
            'data/img/*.png',
            'data/img/*.jpg',
        ]
    },
    data_files=data_files,
    entry_points={
        "console_scripts": [
            "xharvest=xharvest.ui:main"
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
