#from distutils.core import setup

from setuptools import setup, find_packages

setup(
    name='allure2-behave',
    author='Mavlonazarov Daulet',
    url='https://github.com/behave/behave',
    author_email='daul_m@mail.ru',
    version=__import__("allure").__version__,
    #py_modules = ['allure'],
    packages=find_packages(),
    install_requires=['lxml>=3.8.0']
)
