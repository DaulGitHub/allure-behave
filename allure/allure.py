import os, shutil
from time import time
from uuid import uuid4
from lxml import etree


def get_time():
    return str(time())[:14].replace(".", "")


class XMLBuilder(object):
    """XML report files builder"""

    def __init__(self, out_directory_name, suite_name, browser_type, url):
        self._id = str(uuid4())
        self._create_test_suite(suite_name)
        self._create_environment_xml(suite_name, browser_type, url)
        self._scenario_exception = None
        self._report_dir_name = out_directory_name

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

    def _create_environment_xml(self, test_suit_name, browser_type, url):
        """Create environment.xml with
        environment information

        :param browser_type: browser type,
        :param url: host url
        """
        env_params = {'Browser': browser_type, 'URL': url}
        self.environment = etree.Element('root')
        self.environment_id = etree.SubElement(self.environment, 'id')
        self.environment_id.text = self._id
        self.environment_name = etree.SubElement(self.environment, 'name')
        self.environment_name.text = test_suit_name

        for key in env_params:
            self.parameter = etree.SubElement(self.environment, 'parameter')
            self.parameter_name = etree.SubElement(self.parameter, 'name')
            self.parameter_name.text = key
            self.parameter_key = etree.SubElement(self.parameter, 'key')
            self.parameter_key.text = key
            self.parameter_value = etree.SubElement(self.parameter, 'value')
            self.parameter_value.text = env_params[key]

    def create_test_case(self, scenario_name, scenario_steps):
        self._test_case = etree.SubElement(self._test_cases, "test-case", attrib={"start": get_time()})
        name = etree.SubElement(self._test_case, "name")
        name.text = scenario_name
        etree.SubElement(self._test_case, "attachments")
        labels = etree.SubElement(self._test_case, "labels")
        etree.SubElement(labels, "label", attrib={"name": "feature", "value": self._current_feature})
        etree.SubElement(labels, "label", attrib={"name": "story", "value": scenario_name})
        etree.SubElement(labels, "label", attrib={"name": "severity", "value": "normal"})
        etree.SubElement(labels, "label", attrib={"name": "thread", "value": "13110-MainThread"})
        etree.SubElement(labels, "label", attrib={"name": "host", "value": "autotester"})
        self._steps = etree.SubElement(self._test_case, "steps")

        self._scenario_exception = None
        self._scenario_steps = scenario_steps

    def set_scenario_status(self, status):
        """Set scenario status and end time"""
        try:
            stat = status
        except IndexError:
            stat = 'Unknown'

        if not self._test_case.attrib.get("status", None):
            self._test_case.attrib["status"] = stat
        self._test_case.attrib["stop"] = get_time()

        if self._scenario_exception:
            scen_failure = etree.SubElement(self._test_case, "failure")
            scen_failure_msg = etree.SubElement(scen_failure, "message")
            exception_class = self._scenario_exception.__class__.__name__
            scen_failure_msg.text = '{}: {}'.format(exception_class, self._scenario_exception)
            etree.SubElement(scen_failure, "stack-trace")

    def create_step(self, step_name):
        self._step = etree.SubElement(self._steps, "step", attrib={"start": get_time()})
        name = etree.SubElement(self._step, "name")
        name.text = step_name
        title = etree.SubElement(self._step, "title")
        title.text = step_name
        etree.SubElement(self._step, "steps")

    def _set_attachments(self, attachments):
        """Add attachments to step"""
        if attachments is not None:
            attachments_nod = etree.SubElement(self._step, "attachments")
            for attachment in attachments:
                if attachment.get("title"):
                    attach_title = attachment["title"]
                else:
                    raise KeyError("Required key 'title' in attachments items")
                if attachment.get("filename"):
                    attach_file_name = attachment["filename"]
                    attach_file_type = attach_file_name.split(".")[1]
                else:
                    raise KeyError("Required key 'filename' in attachments items")
                attachment = etree.SubElement(attachments_nod, "attachment",
                                              attrib={"title": attach_title, "source": attach_file_name, "type": attach_file_type})

    def set_step_status(self, step, attachments=None):
        steps = self._background_steps + self._scenario_steps  # List of steps in feature

        self._step.attrib["stop"] = get_time()
        try:
            stat = step.status.name
        except IndexError:
            stat = 'unknown'
        self._step.attrib["status"] = stat

        self._set_attachments(attachments)

        if step.exception:  # if step is failed
            self._scenario_exception = step.exception
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

    def create_file_report(self):
        """Write xml report in file"""
        self.suite.attrib["stop"] = get_time()

        out_file_name = "{0}-testsuite.xml".format(self._id)

        with open(os.path.join(self._report_dir_name, out_file_name), "w") as out_file:
            out_file.write(etree.tostring(self.suite, pretty_print=True).decode("utf-8"))

        out_environment_file_name = 'environment.xml'
        with open(os.path.join(self._report_dir_name, out_environment_file_name), "w") as out_file:
            out_file.write(etree.tostring(self.environment, pretty_print=True).decode("utf-8"))

    def set_feature_name(self, name):
        self._current_feature = name

    def set_background_steps(self, steps=[]):
        self._background_steps = steps


class Report(object):
    """Report builder"""

    def __init__(self, out_directory_name, report_name, browser_type, url, re_create=True):
        """Args:
            out_directory_name (str): report directory
            report_name (str): name displayed in report
            browser_type (str): browser type name
            url (str): url test site
            re_create (bool): if True then re-create report folder, else add new unique name
            report files in the report folder
        """

        self.report_dir_name = out_directory_name
        # re-create report dir
        if re_create:
            shutil.rmtree(out_directory_name, True)

        if not os.path.exists(out_directory_name):
            os.makedirs(out_directory_name)

        self._builder = XMLBuilder(out_directory_name, report_name, browser_type, url)

    def before_feature(self, feature):
        """Set feature

        :param feature: feature structure from behave
        """
        self._builder.set_feature_name(feature.name)
        if feature.background is None:
            self._builder.set_background_steps()
        else:
            self._builder.set_background_steps(feature.background.steps)

    def before_scenario(self, scenario):
        """Create scenario

        :param scenario: scenario structure from behave
        """
        self._builder.create_test_case(scenario.name, scenario.steps)

    def after_scenario(self, scenario):
        """Set scenario status

        :param scenario: scenario structure from behave
        """
        self._builder.set_scenario_status(scenario.status.name)

    def before_step(self, step):
        """Create step

        :param step: step structure from behave
        """
        # don`t show internal steps
        if step.location.filename != "<string>":
            self._builder.create_step(step.name)

    def after_step(self, step, attachments=None):
        """After step

        :param step: step structure from behave
        """
        # don`t show internal steps
        if step.location.filename != "<string>":
            self._builder.set_step_status(step, attachments)


    def after_all(self):
        """Create file with report"""
        self._builder.create_file_report()
