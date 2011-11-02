import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from Products.CMFCore.utils import getToolByName

from zest.specialpaste.testing import ZEST_SPECIAL_PASTE_INTEGRATION_TESTING


class TestNormalPaste(unittest.TestCase):

    layer = ZEST_SPECIAL_PASTE_INTEGRATION_TESTING

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
        doc = self._makeOne()
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'private')
        cb = portal.manage_copyObjects(['doc'])
        result = portal.manage_pasteObjects(cb)
        new_id = result[0]['new_id']
        new_doc = portal[new_id]
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'private')

    def testCopyPastePublic(self):
        portal = self.layer['portal']
        wf_tool = getToolByName(portal, 'portal_workflow')
        doc = self._makeOne('publish')
        wf_tool = getToolByName(portal, 'portal_workflow')
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'published')
        cb = portal.manage_copyObjects(['doc'])
        result = portal.manage_pasteObjects(cb)
        new_id = result[0]['new_id']
        new_doc = portal[new_id]
        # This is a normal copy-paste, so the pasted doc should be
        # private.
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'private')
