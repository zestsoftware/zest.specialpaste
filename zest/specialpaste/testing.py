from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from zope.configuration import xmlconfig
from Products.CMFCore.utils import getToolByName


class SpecialPaste(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import zest.specialpaste
        xmlconfig.file('configure.zcml', zest.specialpaste,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        #applyProfile(portal, 'zest.specialpaste:default')
        # Set a default workflow chain.
        wf_tool = getToolByName(portal, 'portal_workflow')
        #wf_tool.setChainForPortalTypes(
        #    ('Document',), 'simple_publication_workflow')
        wf_tool.setDefaultChain('simple_publication_workflow')


ZEST_SPECIAL_PASTE_FIXTURE = SpecialPaste()
ZEST_SPECIAL_PASTE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(ZEST_SPECIAL_PASTE_FIXTURE,), name="SpecialPaste:Integration")
