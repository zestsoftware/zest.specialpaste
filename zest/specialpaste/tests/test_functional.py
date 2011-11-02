import unittest2 as unittest
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import setRoles


class TestDocuments(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def testSetTitle(self):
        portal = self.layer['portal']
        self.assertEqual(portal.Title(), "New title")
