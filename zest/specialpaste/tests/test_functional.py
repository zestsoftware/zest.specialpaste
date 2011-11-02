import unittest2 as unittest

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from zest.specialpaste.testing import (
    ZEST_SPECIAL_PASTE_NOT_INSTALLED_INTEGRATION_TESTING,
    ZEST_SPECIAL_PASTE_INTEGRATION_TESTING,
    make_test_doc,
    make_folder_structure,
    start_traversing,
    )


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

    def testCopyPastePublished(self):
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

    def testObjectCopyPastePublished(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        wf_tool = getToolByName(portal, 'portal_workflow')
        doc = self._makeOne('publish')
        wf_tool = getToolByName(portal, 'portal_workflow')
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'published')
        # Call the skin scripts that would be used when copy-pasting
        # in a browser.
        start_traversing(portal, self.layer['request'])
        portal['doc'].restrictedTraverse('object_copy')()
        portal.restrictedTraverse('object_paste')()
        new_id = 'copy_of_doc'
        new_doc = portal[new_id]
        # This is a normal copy-paste, so the pasted doc should be
        # private.
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'private')

    def testFolderCopyPaste(self):
        # Test copying multiple items, nested, with various review
        # states.
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        make_folder_structure(portal)
        wf_tool = getToolByName(portal, 'portal_workflow')

        main_objects = [
            portal['private-doc'],
            portal['published-doc'],
            portal['private-folder'],
            portal['published-folder'],
            ]
        paths = ['/'.join(obj.getPhysicalPath()) for obj in main_objects]
        request = self.layer['request']
        request.set('paths', paths)
        portal.folder_copy()
        target = portal['target-folder']
        # Sanity check for the cookie with info about the copied objects:
        self.assertTrue(target.cb_dataValid())
        target.folder_paste()
        self.assertEqual(len(target.contentIds()), len(main_objects))

        def get_state(obj):
            return wf_tool.getInfoFor(obj, 'review_state')

        self.assertEqual(get_state(
            target['private-doc']), 'private')
        self.assertEqual(get_state(
            target['published-doc']), 'private')
        self.assertEqual(get_state(
            target['private-folder']), 'private')
        self.assertEqual(get_state(
            target['private-folder']['private-doc']), 'private')
        self.assertEqual(get_state(
            target['private-folder']['published-doc']), 'private')
        self.assertEqual(get_state(
            target['private-folder']['pending-doc']), 'private')
        self.assertEqual(get_state(
            target['private-folder']['published-sub-folder']), 'private')
        self.assertEqual(get_state(
            target['published-folder']), 'private')
        self.assertEqual(get_state(
            target['published-folder']['private-doc']), 'private')
        self.assertEqual(get_state(
            target['published-folder']['published-doc']), 'private')
        self.assertEqual(get_state(
            target['published-folder']['pending-doc']), 'private')
        self.assertEqual(get_state(
            target['published-folder']['private-sub-folder']), 'private')


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
        start_traversing(portal, self.layer['request'])
        portal['doc'].restrictedTraverse('object_copy')()
        portal.restrictedTraverse('@@special-paste')()
        new_id = 'copy_of_doc'
        new_doc = portal[new_id]
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'private')

    def testObjectCopyPastePublished(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        wf_tool = getToolByName(portal, 'portal_workflow')
        doc = self._makeOne('publish')
        wf_tool = getToolByName(portal, 'portal_workflow')
        self.assertEqual(wf_tool.getInfoFor(doc, 'review_state'),
                         'published')
        # Call the skin scripts that would be used when copy-pasting
        # in a browser.
        start_traversing(portal, self.layer['request'])
        portal['doc'].restrictedTraverse('object_copy')()
        portal.restrictedTraverse('@@special-paste')()
        new_id = 'copy_of_doc'
        new_doc = portal[new_id]
        # This is a special copy-paste, so the pasted doc should be
        # published.
        self.assertEqual(wf_tool.getInfoFor(new_doc, 'review_state'),
                         'published')

    def testFolderCopyPaste(self):
        # Test copying multiple items, nested, with various review
        # states.
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        make_folder_structure(portal)
        wf_tool = getToolByName(portal, 'portal_workflow')

        main_objects = [
            portal['private-doc'],
            portal['published-doc'],
            portal['private-folder'],
            portal['published-folder'],
            ]
        paths = ['/'.join(obj.getPhysicalPath()) for obj in main_objects]
        request = self.layer['request']
        request.set('paths', paths)
        portal.folder_copy()
        target = portal['target-folder']
        # Sanity check for the cookie with info about the copied objects:
        self.assertTrue(target.cb_dataValid())
        start_traversing(portal, self.layer['request'])
        target.restrictedTraverse('@@special-paste')()
        self.assertEqual(len(target.contentIds()), len(main_objects))

        def get_state(obj):
            return wf_tool.getInfoFor(obj, 'review_state')

        self.assertEqual(get_state(
            target['private-doc']), 'private')
        self.assertEqual(get_state(
            target['published-doc']), 'published')
        self.assertEqual(get_state(
            target['private-folder']), 'private')
        self.assertEqual(get_state(
            target['private-folder']['private-doc']), 'private')
        self.assertEqual(get_state(
            target['private-folder']['published-doc']), 'published')
        self.assertEqual(get_state(
            target['private-folder']['pending-doc']), 'pending')
        self.assertEqual(get_state(
            target['private-folder']['published-sub-folder']), 'published')
        self.assertEqual(get_state(
            target['published-folder']), 'published')
        self.assertEqual(get_state(
            target['published-folder']['private-doc']), 'private')
        self.assertEqual(get_state(
            target['published-folder']['published-doc']), 'published')
        self.assertEqual(get_state(
            target['published-folder']['pending-doc']), 'pending')
        self.assertEqual(get_state(
            target['published-folder']['private-sub-folder']), 'private')


class TestSetUp(unittest.TestCase):

    layer = ZEST_SPECIAL_PASTE_INTEGRATION_TESTING

    def testActions(self):
        portal = self.layer['portal']
        action_tool = getToolByName(portal, 'portal_actions')
        # This does not work for any action:
        #action_tool.getActionObject('folder_buttons/specialpaste')
        folder_buttons = [action.getId() for action in
                          action_tool.folder_buttons.listActions()]
        self.assertTrue('specialpaste' in folder_buttons)
        object_buttons = [action.getId() for action in
                          action_tool.object_buttons.listActions()]
        self.assertTrue('specialpaste' in object_buttons)

    def testSpecialPasteAvailableWhenInstalled(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        start_traversing(portal, self.layer['request'])
        portal.restrictedTraverse('@@special-paste')

    def testUninstallsCleanly(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        qi = getToolByName(portal, 'portal_quickinstaller')
        qi.uninstallProducts(['zest.specialpaste'])
        start_traversing(portal, self.layer['request'])
        self.assertRaises(AttributeError,
                          portal.restrictedTraverse,
                          ('@@special-paste',))
        action_tool = getToolByName(portal, 'portal_actions')
        folder_buttons = [action.getId() for action in
                          action_tool.folder_buttons.listActions()]
        self.assertFalse('specialpaste' in folder_buttons)
        object_buttons = [action.getId() for action in
                          action_tool.object_buttons.listActions()]
        self.assertFalse('specialpaste' in object_buttons)


class TestNotInstalled(unittest.TestCase):

    layer = ZEST_SPECIAL_PASTE_NOT_INSTALLED_INTEGRATION_TESTING

    def testSpecialPasteNotAvailableWhenNotInstalled(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ('Manager',))
        start_traversing(portal, self.layer['request'])
        self.assertRaises(AttributeError,
                          portal.restrictedTraverse,
                          ('@@special-paste',))
