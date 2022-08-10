from setuptools import setup, find_packages
import os
import platform
from glob import glob
from pkg_resources import parse_requirements
from pybind11.setup_helpers import Pybind11Extension

lib_path = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.join(lib_path, 'requirements.txt')

with open(requirements_path) as f:
    install_requires = list(map(str, parse_requirements(f)))

ext_modules = [
    Pybind11Extension(
        "_pfutil",
        sorted(glob("pfutils-cpp/src/*.cpp")),
        cxx_std=17,
    )
]

setup(
    name='pfutils',
    version='0.0.25',
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
    ext_modules=ext_modules,
    include_package_data=True,
    install_requires=install_requires,
)
