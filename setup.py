import os.path
from setuptools import setup, find_packages
from xharvest import __version__

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='xharvest',
    version=__version__,
    url='https://github.abc.com/vyscond/python-xharvest',
    description='Unofficial GTK based Harvest desktop app for Linux',
    long_description=long_description,
    install_requires=[
        'pycairo==1.19.1',
        'PyGObject==3.34.0',
        'keyring==21.2.0',
        'harvest-api==0.2.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['glade/*.glade']},
    data_files = [
        (os.path.expanduser('~/.local/share/applications'), ['data/org.velvetkeyboad.xHarvest.desktop']),
        (os.path.expanduser('~/.local/share/icons/hicolor/48x48/apps/'), ['data/xharvest.png']),
        (os.path.expanduser('~/.local/share/icons/hicolor/32x32/apps/'), ['data/xharvest.png']),
        (os.path.expanduser('~/.local/share/icons/hicolor/16x16/apps/'), ['data/xharvest.png']),
    ],
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
