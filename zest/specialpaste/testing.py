from Products.CMFCore.utils import getToolByName
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig
from zope.event import notify
try:
    from zope.traversing.interfaces import BeforeTraverseEvent
    BeforeTraverseEvent  # pyflakes
except ImportError:
    # BBB for Zope 2.12
    from zope.app.publication.interfaces import BeforeTraverseEvent


class SpecialPasteNotInstalled(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import zest.specialpaste
        xmlconfig.file('configure.zcml', zest.specialpaste,
                       context=configurationContext)


class SpecialPaste(SpecialPasteNotInstalled):

    defaultBases = (PLONE_FIXTURE,)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'zest.specialpaste:default')
        # Set a default workflow chain.
        wf_tool = getToolByName(portal, 'portal_workflow')
        wf_tool.setDefaultChain('simple_publication_workflow')


ZEST_SPECIAL_PASTE_NOT_INSTALLED_FIXTURE = SpecialPasteNotInstalled()
ZEST_SPECIAL_PASTE_NOT_INSTALLED_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZEST_SPECIAL_PASTE_NOT_INSTALLED_FIXTURE,),
    name="SpecialPasteNotInstalled:Integration")

ZEST_SPECIAL_PASTE_FIXTURE = SpecialPaste()
ZEST_SPECIAL_PASTE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZEST_SPECIAL_PASTE_FIXTURE,), name="SpecialPaste:Integration")

# A few helper functions.


def make_test_doc(portal, transition=None):
    new_id = portal.invokeFactory('Document', 'doc')
    doc = portal[new_id]
    if transition is not None:
        wf_tool = getToolByName(portal, 'portal_workflow')
        wf_tool.doActionFor(doc, transition)
    return doc


def make_folder_structure(portal):
    """Make a demo folder structure with some documents.
    """
    wf_tool = getToolByName(portal, 'portal_workflow')

    # documents in portal
    portal.invokeFactory('Document', 'private-doc')
    portal.invokeFactory('Document', 'published-doc')
    wf_tool.doActionFor(portal['published-doc'], 'publish')

    # private folder
    portal.invokeFactory('Folder', 'private-folder')
    folder = portal['private-folder']
    folder.invokeFactory('Document', 'private-doc')
    folder.invokeFactory('Document', 'published-doc')
    wf_tool.doActionFor(folder['published-doc'], 'publish')
    folder.invokeFactory('Document', 'pending-doc')
    wf_tool.doActionFor(folder['pending-doc'], 'submit')
    folder.invokeFactory('Folder', 'published-sub-folder')
    wf_tool.doActionFor(folder['published-sub-folder'], 'publish')

    # published folder
    portal.invokeFactory('Folder', 'published-folder')
    folder = portal['published-folder']
    wf_tool.doActionFor(folder, 'publish')
    folder.invokeFactory('Document', 'private-doc')
    folder.invokeFactory('Document', 'published-doc')
    wf_tool.doActionFor(folder['published-doc'], 'publish')
    folder.invokeFactory('Document', 'pending-doc')
    wf_tool.doActionFor(folder['pending-doc'], 'submit')
    folder.invokeFactory('Folder', 'private-sub-folder')

    # target folder for pasting into.
    portal.invokeFactory('Folder', 'target-folder')


def start_traversing(object, request):
    # This makes sure plone.browserlayer is activated.
    notify(BeforeTraverseEvent(object, request))
