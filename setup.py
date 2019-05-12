from setuptools import setup, find_packages
import allure

setup(
    name = 'allure-behave',
    author = 'Mavlonazarov Daulet',
    author_email = 'daul_m@mail.ru',
    version = allure.__version__,
    #py_modules = ['allure'],
    packages=find_packages(),
    install_requires=['lxml>=3.8.0']
)
