from setuptools import setup, find_packages

setup(
    name='xharvest',
    packages=find_packages(),
    url='https://github.abc.com/vyscond/xharvest',
    description='Unofficial GTK based Harvest desktop app',
    long_description=open('README.md').read(),
    install_requires=[
        'pycairo==1.19.1',
		'PyGObject==3.34.0',
    ],
    dependency_links=[
        'http://github.com/vyscond/python-harvest/tarball/master#egg=package-1.0',
    ],
    include_package_data=True,
)
