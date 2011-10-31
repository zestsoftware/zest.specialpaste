from Acquisition import aq_inner
from Products.Five import BrowserView
#from AccessControl import Unauthorized
#from ZODB.POSException import ConflictError
from Products.statusmessages.interfaces import IStatusMessage
from OFS.CopySupport import CopyError
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from Products.CMFPlone import PloneMessageFactory as PMF

from zest.specialpaste.interfaces import ISpecialPasteInProgress


class SpecialPaste(BrowserView):
    """Special paste copied objects.

    Idea:

    - Mark the request with an extra interface.

    - Catch the ObjectCopiedEvent and store extra info about that on the request.

    - Catch the ObjectClonedEvent and set the workflow there.

    The idea is also that I do not like the idea of copying and
    adapting the large manage_pasteObjects method from
    OFS.CopySupport...

    """

    def __call__(self):
        """Do special paste.

        This is mostly a copy of
        Products/CMFPlone/skins/plone_scripts/object_paste.cpy
        """
        context = aq_inner(self.context)
        request = self.request
        add_message = IStatusMessage(request).add
        msg_type = 'error'  # Most messages are errors
        if context.cb_dataValid():
            # Mark the request with an interface that the event handlers
            # react on.
            alsoProvides(self.request, ISpecialPasteInProgress)
            try:
                context.manage_pasteObjects(self.request['__cp'])
                transaction_note('Pasted content to %s' % (context.absolute_url()))
                msg = PMF(u'Item(s) pasted.')
                msg_type = 'info'
            except ConflictError:
                raise
            except ValueError:
                msg = PMF(u'Disallowed to paste item(s).')
            except Unauthorized:
                msg = PMF(u'Unauthorized to paste item(s).')
            except: # fallback
                msg = PMF(u'Paste could not find clipboard content.')
        else:
            msg = PMF(u'Copy or cut one or more items to paste.')
        add_message(msg, type='error')
        request.response.redirect(context.absolute_url())
        return ''
