from AccessControl import Unauthorized
from Acquisition import aq_inner
#from OFS.CopySupport import CopyError
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
#from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from zest.specialpaste.interfaces import ISpecialPasteInProgress


class SpecialPaste(BrowserView):
    """Special paste copied objects.

    Idea:

    - Mark the request with an extra interface.

    - Catch the ObjectCopiedEvent and store extra info about that on
      the request.

    - Catch the ObjectClonedEvent and set the workflow there.

    The idea is also that I do not like the idea of copying and
    adapting the large manage_pasteObjects method from
    OFS.CopySupport...

    """

    def __call__(self):
        """Do special paste.

        It looks like the only thing we actually need to do is mark
        the request and let object_paste (or folder_paste) do the
        heavy lifting.

        Oh, object_paste and folder_paste actually do exactly the same
        thing, so that is easy.

        Possibly we should add a form in between that asks the user
        how special the paste must be (keep workflow state, keep local
        roles, etc).  For now we only handle the workflow state
        though.
        """
        context = aq_inner(self.context)
        alsoProvides(self.request, ISpecialPasteInProgress)
        return context.restrictedTraverse('object_paste')()
