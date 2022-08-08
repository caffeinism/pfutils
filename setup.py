from setuptools import setup, find_packages
import os
import platform
from pkg_resources import parse_requirements

lib_path = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.join(lib_path, 'requirements.txt')

with open(requirements_path) as f:
    install_requires = list(map(str, parse_requirements(f)))


setup(
    name='pfutils',
    version='0.0.24',
    description='parallel file utility command line tool',
    license='MIT',
    packages=[*find_packages()],
    author='Kim Minjong',
    author_email='make.dirty.code@gmail.com',
    keywords=['ceph', 'nfs'],
    url='https://github.com/caffeinism/pfutils',
    entry_points = {
        'console_scripts': ['pfutils=pfutils.main:entrypoint'],
    },
    include_package_data=True,
    install_requires=install_requires,
)
