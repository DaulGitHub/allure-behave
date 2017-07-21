from allure.allure import ReportBuilder


def before_all(context):
    context.allure = ReportBuilder("Tests Dispatch system")
    pass


def before_feature(context, feature):
    context.allure.current_feature = feature.name
    pass


def before_scenario(context, scenario):
    context.allure.before_scenario(scenario.name)
    pass


def before_step(context, step):
    context.allure.before_step(step.name)
    pass


def after_step(context, step):
    context.allure.after_step(step.status)
    pass


def after_scenario(context, scenario):
    context.allure.after_scenario(scenario.status)
    pass


def after_feature(context, feature):
    pass


def after_all(context):
    context.allure.after_all()
    pass
