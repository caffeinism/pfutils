from setuptools import setup, find_packages
import os
import platform

lib_path = os.path.dirname(os.path.realpath(__file__))
requirements_path = os.path.join(lib_path, 'requirements.txt')

install_requires = [] 
if os.path.isfile(requirements_path):
    with open(requirements_path) as f:
        install_requires = f.read().splitlines()
        

setup(
    name='pfutils',
    version='0.0.1',
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
