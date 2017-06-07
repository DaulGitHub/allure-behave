from time import time
import os, shutil
from uuid import uuid4
from lxml import etree


def get_time():
    return str(time())[:14].replace(".", "")


class ReportBuilder(object):
    current_feature = ""

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

    def before_scenario(self, scenario_name):
        """Create scenario

        :param scenario_name: scenario name
        """
        self._test_case = etree.SubElement(self._test_cases, "test-case", attrib={"start": get_time()})
        name = etree.SubElement(self._test_case, "name")
        etree.SubElement(self._test_case, "attachments")
        name.text = scenario_name
        labels = etree.SubElement(self._test_case, "labels")
        etree.SubElement(labels, "label", attrib={"name": "feature", "value": self.current_feature})
        etree.SubElement(labels, "label", attrib={"name": "story", "value": scenario_name})
        etree.SubElement(labels, "label", attrib={"name": "severity", "value": "normal"})
        etree.SubElement(labels, "label", attrib={"name": "thread", "value": "13110-MainThread"})
        etree.SubElement(labels, "label", attrib={"name": "host", "value": "autotester"})
        self._steps = etree.SubElement(self._test_case, "steps")

    def after_scenario(self, status):
        """Set scenario status and end time

        :param status: scenario execution status
        """
        self._test_case.attrib["status"] = status
        self._test_case.attrib["stop"] = get_time()

    def before_step(self, step_name):
        """Create step

        :param step_name: step name
        """
        self._step = etree.SubElement(self._steps, "step", attrib={"start": get_time()})
        name = etree.SubElement(self._step, "name")
        name.text = step_name
        title = etree.SubElement(self._step, "title")
        title.text = step_name
        etree.SubElement(self._step, "attachments")
        etree.SubElement(self._step, "steps")

    def after_step(self, status):
        """Set step status and ena time

        :param status: step execution status
        """
        self._step.attrib["stop"] = get_time()
        self._step.attrib["status"] = status

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
