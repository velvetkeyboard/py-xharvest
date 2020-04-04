from setuptools import setup, find_packages
from xharvest import __version__


setup(
    name='xharvest',
    version=__version__,
    url='https://github.abc.com/vyscond/python-xharvest',
    description='Unofficial GTK based Harvest desktop app for Linux',
    long_description=open('README.md').read(),
    install_requires=[
        'pycairo==1.19.1',
        'PyGObject==3.34.0',
        'keyring==21.2.0',
        'harvest-api==0.2.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['glade/*.glade']},
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
