import os.path
from setuptools import setup, find_packages
from xharvest import __version__

data_path = f"{os.path.expanduser('~')}/.local/share"
xharvest_cfg_path = f"{os.path.expanduser('~')}/.xharvest"

with open('README.md', 'r') as f:
    long_description = f.read()

data_files = [
    (f'{xharvest_cfg_path}', ['data/user_avatar.jpg']),
    (f'{data_path}/applications', ['data/org.velvetkeyboad.xHarvest.desktop']),
    (
        f'{data_path}/icons/hicolor/128x128/apps/',
        ['data/hicolor/128x128/xharvest.png']
    ),
    (
        f'{data_path}/icons/hicolor/48x48/apps/',
        ['data/hicolor/48x48/xharvest.png']
    ),
    (
        f'{data_path}/icons/hicolor/32x32/apps/',
        ['data/hicolor/32x32/xharvest.png']
    ),
    (
        f'{data_path}/icons/hicolor/16x16/apps/',
        ['data/hicolor/16x16/xharvest.png']
    ),
]

setup(
    name='xharvest',
    version=__version__,
    url='https://github.com/vyscond/py-xharvest',
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
