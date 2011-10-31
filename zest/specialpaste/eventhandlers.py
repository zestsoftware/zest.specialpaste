import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.annotation.interfaces import IAnnotations

from zest.specialpaste.interfaces import ISpecialPasteInProgress

logger = logging.getLogger(__name__)
ANNO_KEY = 'zest.specialpaste.original'


def update_copied_objects_list(object, event):
    """Update the list of which objects have been copied.

    Note that the new object does not yet have an acquisition chain,
    so we cannot really do much here yet.  We are only interested in
    the old object now.

    Note: this might be called too many times.
    """
    request = event.original.REQUEST
#    if not ISpecialPasteInProgress.providedBy(request):
#        return
    annotations = IAnnotations(object, None)
    if annotations is None:
        logger.warn("Annotations on object not supported: "
                    "zest.specialpaste will not work.")
        return
    annotations[ANNO_KEY] = event.original.getPhysicalPath()
    logger.info("Annotation set.")


def update_cloned_object(object, event):
    """Update the cloned object.

    Now the new (cloned) object has an acquisition chain and we can
    start doing interesting things to it, based on the info of the old
    object.
    """
    request = object.REQUEST
#    if not ISpecialPasteInProgress.providedBy(request):
#        return
    annotations = IAnnotations(object, None)
    if annotations is None:
        logger.info("No annotations.")
        return
    original_path = annotations.get(ANNO_KEY, None)
    if not original_path:
        logger.info("No original found.")
        return
    logger.info("Original found: %r", original_path)
    # We could delete our annotation, but it does not hurt to keep it
    # and it may hurt to remove it when others write subscribers that
    # depend on it.
    #
    # del annotations[ANNO_KEY]
    original_object = object.restrictedTraverse('/'.join(original_path))
    wf_tool = getToolByName(object, 'portal_workflow')
    try:
        original_state = wf_tool.getInfoFor(original_object, 'review_state')
    except WorkflowException:
        return
