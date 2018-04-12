import os
import shutil
from allure.allure import Report


def before_all(context):
    browser_type = "firefox"
    base_url = "https://mytests.ru"

    report_dir_name = "allure-report"
    context.allure = Report(report_dir_name, "Tests Dispatch system", browser_type, base_url, re_create=True)

    container_dir = "temp_files"
    attachments = get_attachments()
    shutil.copy(os.path.join(container_dir, attachments[0]["filename"]), report_dir_name)
    shutil.copy(os.path.join(container_dir, attachments[1]["filename"]), report_dir_name)


def before_feature(context, feature):
    context.allure.before_feature(feature)


def before_scenario(context, scenario):
    context.allure.before_scenario(scenario)


def before_step(context, step):
    context.allure.before_step(step)


def after_step(context, step):
    context.allure.after_step(step, get_attachments())


def after_scenario(context, scenario):
    context.allure.after_scenario(scenario)


def after_feature(context, feature):
    pass


def after_all(context):
    context.allure.after_all()


def get_attachments():
    attachments = [{"title": "My attachment file1", "filename": "b716cbcc-fc87-47e5-b188-5cd001b7e179.txt"},
                   {"title": "My attachment file2", "filename": "b83f9742-aeab-4044-aca0-3e2456b957e3.jpg"}]

    return attachments
