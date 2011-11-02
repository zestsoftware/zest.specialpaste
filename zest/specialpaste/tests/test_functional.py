import unittest2 as unittest

from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from Products.CMFCore.utils import getToolByName


class TestNormalPaste(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def _makeOne(self, transition=None):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        new_id = portal.invokeFactory('Document', 'doc')
        doc = portal[new_id]
        if transition is not None:
            wf_tool = getToolByName(portal, 'portal_workflow')
            wf_tool.doActionFor(doc, transition)
        return doc

    def testCopyPastePrivate(self):
        portal = self.layer['portal']
        wf_tool = getToolByName(portal, 'portal_workflow')
        wf_tool.setChainForPortalTypes(
            ('Document',), 'simple_publication_workflow')
        doc = self._makeOne()
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'), 'private')

    def testCopyPastePublic(self):
        portal = self.layer['portal']
        wf_tool = getToolByName(portal, 'portal_workflow')
        wf_tool.setChainForPortalTypes(
            ('Document',), 'simple_publication_workflow')
        doc = self._makeOne('publish')
        wf_tool = getToolByName(portal, 'portal_workflow')
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'), 'published')
