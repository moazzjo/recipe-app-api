"""
simple test

"""

from django.test import SimpleTestCase

from app import calc


class TestCalc(SimpleTestCase):

    def testAdd(self):
        res = calc.add(3, 7)

        self.assertEqual(res, 10)
