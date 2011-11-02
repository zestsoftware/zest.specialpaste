import logging

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.annotation.interfaces import IAnnotations

from zest.specialpaste.interfaces import ISpecialPasteInProgress

logger = logging.getLogger(__name__)
ANNO_KEY = 'zest.specialpaste.original'
_marker = object()


def update_copied_objects_list(object, event):
    """Update the list of which objects have been copied.

    Note that the new object does not yet have an acquisition chain,
    so we cannot really do much here yet.  We are only interested in
    the old object now.

    Note: this might be called too many times.

    When a folder with document is copied, one event is sent for the
    folder and one for the document.  The document one is special:

    - object is copy of document

    - event.object is copy of folder

    - event.original is original folder

    Both copies have not been added to an acquisition context yet.
    """
    request = event.original.REQUEST
    if not ISpecialPasteInProgress.providedBy(request):
        return
    annotations = IAnnotations(object, None)
    if annotations is None:
        logger.warn("Annotations on object not supported: "
                    "zest.specialpaste will not work.")
        return
    if object is event.object:
        original = event.original
    else:
        original = event.original[object.getId()]
    annotations[ANNO_KEY] = original.getPhysicalPath()
    logger.info("Annotation set.")


def update_cloned_object(object, event):
    """Update the cloned object.

    Now the new (cloned) object has an acquisition chain and we can
    start doing interesting things to it, based on the info of the old
    object.
    """
    request = object.REQUEST
    if not ISpecialPasteInProgress.providedBy(request):
        return
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
    wfs = wf_tool.getWorkflowsFor(original_object)
    if wfs is None:
        return
    for wf in wfs:
        if not wf.isInfoSupported(original_object, 'review_state'):
            continue
        original_state = wf.getInfoFor(original_object, 'review_state',
                                       _marker)
        if original_state is _marker:
            continue

        # We need to store a real status on the new object.
        former_status = wf_tool.getStatusOf(wf.id, original_object)
        if former_status is None:
            former_status = {}
        # Use a copy for good measure
        status = former_status.copy()

        # We could fire a BeforeTransitionEvent and an
        # AfterTransitionEvent, but that does not seem wise, as we do
        # not want to treat this as a transition at all.
        try:
            wf_tool.setStatusOf(wf.id, object, status)
        except WorkflowException:
            logger.warn("WorkflowException when setting review state of "
                        "cloned object %r to %s.", object, original_state)
        else:
            logger.info("Setting review state of cloned "
                        "object %r to %s.", object, original_state)
            # Update role to permission assignments.
            wf.updateRoleMappingsFor(object)

    # Update the catalog, especially the review_state.
    # object.reindexObjectSecurity() does not help though.
    object.reindexObject(idxs='review_state')
