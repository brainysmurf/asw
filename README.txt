About AppleScriptWrapper
===============

AppleScriptWrapper is a very high-level utility package that makes
scripting AppleScript in Python even easier.


Requirements
------------

AppleScriptWrapper depends on appscript, which supports Python 2.3 to 2.7, 
and Python 3.1 and later.

Appscript requires Mac OS X 10.4 or later.


Installation
------------

AppleScriptWrapper is packaged using the standard Python Distribution Utilities 
(a.k.a. Distutils). To install appscript, cd to the asw directory and run:

  python3 setup.py install

Setuptools/Distribute (available from <http://cheeseshop.python.org/pypi>) 
will be used if installed, otherwise setup.py will revert to Distutils.

Building appscript from source requires the gcc compiler supplied with 
Apple's Xcode IDE. Xcode can be obtained from Mac OS X installer disks
or <http://developer.apple.com>.


Usage
-----

from AppleScriptWrapper.Basic import get_app
pages = get_app("Pages")      	# Same string as tell app ""
dir(pages)			# peruse lots and lots of methods


Copyright
---------

AppleScriptWrapper is released into the public domain.
Author is Adam Ryan Morris
amorris@mistermorris.com
