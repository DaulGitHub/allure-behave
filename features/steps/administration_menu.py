from behave import step
from time import sleep


@step('Hello step1')
def step_impl(context):
    sleep(1)

@step('Hello step2')
def step_impl(context):
    raise AssertionError()

