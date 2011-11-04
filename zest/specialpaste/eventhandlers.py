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

    When copying a single item:

    - object is copy of item

    - event.object is copy of item

    - event.original is original item

    Both copies have not been added to an acquisition context yet.

    When copying a folder that has sub folders with content, like
    folder/sub/doc, and pasting it to the same location so the origal
    and pasted folders are at the same level, this event is also fired
    with:

    - object is copy of doc, with physical path copy_of_folder/sub/doc

    - event.object is copy of folder, with physical path copy_of_folder

    - event.original is the original folder

    - sub is nowhere to be seen...

    Luckily we can use physical paths in that case.
    """
    request = event.original.REQUEST
    if not ISpecialPasteInProgress.providedBy(request):
        return
    annotations = IAnnotations(object, None)
    if annotations is None:
        # Annotations on this object are not supported.  This happens
        # e.g. for SyndicationInformation, ATSimpleStringCriterion,
        # and WorkflowPolicyConfig, so it is quite normal.
        return
    if object is event.object:
        original = event.original
    else:
        # Use the path minus the top level folder, as that may be
        # copy_of_folder.
        path = '/'.join(object.getPhysicalPath()[1:])
        try:
            original = event.original.restrictedTraverse(path)
        except:
            logger.error("Could not get original %s from parent %r", path,
                event.original)
            raise
    annotations[ANNO_KEY] = original.getPhysicalPath()
    logger.debug("Annotation set: %r", '/'.join(original.getPhysicalPath()))


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
        logger.debug("No annotations.")
        return
    original_path = annotations.get(ANNO_KEY, None)
    if not original_path:
        logger.debug("No original found.")
        return
    logger.debug("Original found: %r", original_path)
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
            logger.debug("Setting review state of cloned "
                         "object %r to %s.", object, original_state)
            # Update role to permission assignments.
            wf.updateRoleMappingsFor(object)

    # Update the catalog, especially the review_state.
    # object.reindexObjectSecurity() does not help though.
    object.reindexObject(idxs='review_state')
