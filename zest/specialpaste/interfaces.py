from zope.interface import Interface


class ISpecialPasteInProgress(Interface):
    """Marker interface on a request when a special paste is in progress.
    """


class IZestSpecialPasteLayer(Interface):
    """Browser layer marker interface.

    plone.browserlayer adds this to the request when our package is
    installed in the Plone Site.
    """
