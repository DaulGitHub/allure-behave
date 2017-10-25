from behave import step
from time import sleep


@step('My background step')
def step_impl(context):
    context.execute_steps("""
        When My internal step
    """)
    sleep(0.1)


@step('Hello step1')
def step_impl(context):
    sleep(0.1)


@step('Hello step2')
def step_impl(context):
    assert False, "My test Error message"


@step('Hello step3')
def step_impl(context):
    1/0
    sleep(0.1)


@step('Step with internal step')
def step_impl(context):
    context.execute_steps("""
        When My internal step
    """)
    sleep(0.1)


@step('My internal step')
def step_impl(context):
    sleep(0.1)
