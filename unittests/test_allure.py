from unittest import TestCase
from allure.allure import get_time


class TestXMLBuilder(TestCase):

    def test_get_time(self):

        current_time = get_time()
        self.assertEqual(type(current_time), str)
        self.assertEqual(len(current_time), 13)
