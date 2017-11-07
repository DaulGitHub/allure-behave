import os
from allure.allure import Report


def before_all(context):
    browser_type = "firefox"
    base_url = "https://mytests.ru"
    context.allure = Report("Tests Dispatch system", browser_type, base_url)


def before_feature(context, feature):
    context.allure.before_feature(feature)


def before_scenario(context, scenario):
    context.allure.before_scenario(scenario)


def before_step(context, step):
    context.allure.before_step(step)


def after_step(context, step):
    context.allure.after_step(step)


def after_scenario(context, scenario):
    context.allure.after_scenario(scenario)


def after_feature(context, feature):
    pass

def after_all(context):
    report_dir_name = "allure-report-1"
    if os.path.exists(report_dir_name):
        report_dir_name = "allure-report-2"
    context.allure.after_all(report_dir_name)
