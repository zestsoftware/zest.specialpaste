.. contents::
..
    Contents


Introduction
------------

When copying and pasting an object in Plone the workflow state of the
newly pasted object is set to the initial state.  Sometimes you want
to keep the original state.  This is what ``zest.specialpaste`` does.


Use case
--------

You use Plone to store some information about clients in a folder.
You have created a standard folder with a few sub folders and several
documents, images and files that you use as a template for new
clients.  For new clients some of these objects should already be
published.  You have set this up correctly in the template or sample
folder.  You copy this folder, go to a new location and use the
'Special paste' action from ``zest.specialpaste`` to paste the objects
and let the review state of the new objects be the same as their
originals.


Compatibility
-------------

Tested on Plone 4.1.2.  Should work fine on 4.0 as well, and probably
3.3 too.


Installation
------------

- Add ``zest.specialpaste`` to the ``eggs`` of your buildout (and to
  the ``zcml`` too if you are on Plone 3.2 or earlier).  Rerun the
  buildout.

- Install Zest Special Paste in the Add-on Products control panel.
  This adds a 'Special paste' action on objects.


Future ideas
------------

- We can add a form in between where you can specify what should be
  special for the paste.  When selecting no options it should do the
  same as the standard paste action.

- Allow keeping the original owner.

- Take over local roles.


TODO
----

- Test compatibility with earlier Plones.

- Also add this action in the folder_contents.
