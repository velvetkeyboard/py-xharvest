from setuptools import setup, find_packages

setup(
    name='xharvest',
    packages=find_packages(),
    url='https://github.abc.com/vyscond/python-xharvest',
    description='Unofficial GTK based Harvest desktop app for Linux',
    long_description=open('README.md').read(),
    install_requires=[
        'pycairo==1.19.1',
        'PyGObject==3.34.0',
        'harvest-api==0.2.0',
    ],
    include_package_data=True,
)
