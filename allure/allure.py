import os, shutil

from time import time
from uuid import uuid4
from lxml import etree


def get_time():
    return str(time())[:14].replace(".", "")


class ReportBuilder(object):
    _scenario_steps = []

    def __init__(self, suite_name):
        self._create_test_suite(suite_name)

    def _create_test_suite(self, name):
        """Create test-suite

        :param name: suite name
        """
        NAMESPACE = "urn:model.allure.qatools.yandex.ru"
        NS = "{%s}" % NAMESPACE
        NSMAP = {"ns0": NAMESPACE}
        self.suite = etree.Element(NS + "test-suite", attrib={"start": get_time()}, nsmap=NSMAP)
        suite_name = etree.SubElement(self.suite, "name")
        suite_name.text = name
        etree.SubElement(self.suite, "labels")
        self._test_cases = etree.SubElement(self.suite, "test-cases")

    def before_scenario(self, scenario):
        """Create scenario

        :param scenario: scenario
        """
        self._test_case = etree.SubElement(self._test_cases, "test-case", attrib={"start": get_time()})
        name = etree.SubElement(self._test_case, "name")
        scenario_name = scenario.name
        name.text = scenario_name
        etree.SubElement(self._test_case, "attachments")
        labels = etree.SubElement(self._test_case, "labels")
        etree.SubElement(labels, "label", attrib={"name": "feature", "value": self.current_feature})
        etree.SubElement(labels, "label", attrib={"name": "story", "value": scenario_name})
        etree.SubElement(labels, "label", attrib={"name": "severity", "value": "normal"})
        etree.SubElement(labels, "label", attrib={"name": "thread", "value": "13110-MainThread"})
        etree.SubElement(labels, "label", attrib={"name": "host", "value": "autotester"})
        self._steps = etree.SubElement(self._test_case, "steps")

        self.scenario_exception = None
        self._scenario_steps = scenario.steps

    def after_scenario(self, status):
        """Set scenario status and end time

        :param status: scenario execution status
        """
        try:
            stat = status.split('.')[1]
        except IndexError:
            stat = 'Unknown'

        if not self._test_case.attrib.get("status", None):
            self._test_case.attrib["status"] = stat
        self._test_case.attrib["stop"] = get_time()

        if self.scenario_exception:
            scen_failure = etree.SubElement(self._test_case, "failure")
            scen_failure_msg = etree.SubElement(scen_failure, "message")
            exception_class = self.scenario_exception.__class__.__name__
            scen_failure_msg.text = '{}: {}'.format(exception_class, self.scenario_exception)
            scen_failure_stack_trace = etree.SubElement(scen_failure, "stack-trace")

    def before_step(self, step_name):
        """Create step

        :param step_name: step name
        """
        if hasattr(self, 'background'):
            steps = self.background.steps + self._scenario_steps  # List of steps in feature
        else:
            steps = self._scenario_steps

        for item in steps:
            if step_name == item.name:
                self._step = etree.SubElement(self._steps, "step", attrib={"start": get_time()})
                name = etree.SubElement(self._step, "name")
                name.text = step_name
                title = etree.SubElement(self._step, "title")
                title.text = step_name
                etree.SubElement(self._step, "attachments")
                etree.SubElement(self._step, "steps")
                break

    def after_step(self, step):
        """Set step status and ena time

        :param step: step
        """

        if hasattr(self, 'background'):
            steps = self.background.steps + self._scenario_steps  # List of steps in feature
        else:
            steps = self._scenario_steps
        
        for item in steps:
            if step.name == item.name:
                self._step.attrib["stop"] = get_time()
                try:
                    stat = str(step.status).split('.')[1]
                except IndexError:
                    stat = 'unknown'
                self._step.attrib["status"] = stat

                if step.exception:  # if step is failed
                    self.scenario_exception = step.exception
                    if not step.exception.__class__.__name__ == "AssertionError":
                        self._step.attrib["status"] = 'broken'
                        self._test_case.attrib["status"] = 'broken'
                    step_index = steps.index(step)
                    skipped_steps = steps[step_index + 1:]

                    for step in skipped_steps:
                        skipped_step = etree.SubElement(self._steps, "step", attrib={"start": get_time()})
                        name = etree.SubElement(skipped_step, "name")
                        name.text = step.name
                        title = etree.SubElement(skipped_step, "title")
                        title.text = step.name
                        skipped_step.attrib['status'] = "skipped"
                break

    def after_all(self):
        """Write xml report in file"""

        self.suite.attrib["stop"] = get_time()

        # re-create report dir
        out_directory = "allure-report"
        shutil.rmtree(out_directory, True)
        if not os.path.exists(out_directory):
            os.makedirs(out_directory)
        out_file_name = "{0}-testsuite.xml".format(str(uuid4()))

        with open(os.path.join(out_directory, out_file_name), "w") as out_file:
            out_file.write(etree.tostring(self.suite, pretty_print=True).decode("utf-8"))
