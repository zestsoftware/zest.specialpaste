import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from zest.specialpaste.testing import ZEST_SPECIAL_PASTE_INTEGRATION_TESTING
from zest.specialpaste.testing import make_test_doc


class TestNormalPaste(unittest.TestCase):

    layer = ZEST_SPECIAL_PASTE_INTEGRATION_TESTING

    def _makeOne(self, transition=None):
        return make_test_doc(self.layer['portal'], transition)

    def testCopyPastePrivate(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
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
        setRoles(portal, TEST_USER_ID, ('Manager',))
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

    def testObjectCopyPastePublic(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        wf_tool = getToolByName(portal, 'portal_workflow')
        doc = self._makeOne('publish')
        wf_tool = getToolByName(portal, 'portal_workflow')
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'published')
        # Call the skin scripts that would be used when copy-pasting
        # in a browser.
        portal['doc'].restrictedTraverse('object_copy')()
        portal.restrictedTraverse('object_paste')()
        new_id = 'copy_of_doc'
        new_doc = portal[new_id]
        # This is a normal copy-paste, so the pasted doc should be
        # private.
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'private')

    def TODOtestFolderCopyPaste(self):
        # Test copying multiple items, possibly nested, with various
        # review states.
        pass


class TestSpecialPaste(unittest.TestCase):

    layer = ZEST_SPECIAL_PASTE_INTEGRATION_TESTING

    def _makeOne(self, transition=None):
        return make_test_doc(self.layer['portal'], transition)

    def testCopyPastePrivate(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        wf_tool = getToolByName(portal, 'portal_workflow')
        doc = self._makeOne()
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'private')
        # Call the skin scripts that would be used when copy-pasting
        # in a browser.
        portal['doc'].restrictedTraverse('object_copy')()
        portal.restrictedTraverse('@@special-paste')()
        new_id = 'copy_of_doc'
        new_doc = portal[new_id]
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'private')

    def testObjectCopyPastePublic(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        wf_tool = getToolByName(portal, 'portal_workflow')
        doc = self._makeOne('publish')
        wf_tool = getToolByName(portal, 'portal_workflow')
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'published')
        # Call the skin scripts that would be used when copy-pasting
        # in a browser.
        portal['doc'].restrictedTraverse('object_copy')()
        portal.restrictedTraverse('@@special-paste')()
        new_id = 'copy_of_doc'
        new_doc = portal[new_id]
        # This is a special copy-paste, so the pasted doc should be
        # published.
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'published')

    def TODOtestFolderCopyPaste(self):
        # Test copying multiple items, possibly nested, with various
        # review states.
        pass
