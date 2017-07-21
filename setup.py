#from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name = 'allure-behave',
    author = 'Mavlonazarov Daulet',
    author_email = 'daul_m@mail.ru',
    version = '1.0',
    #py_modules = ['allure'],
    packages=find_packages(),
    install_requires=['lxml>=3.8.0']
)
