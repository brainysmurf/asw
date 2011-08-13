try:
	from setuptools import setup
except ImportError:
	print("Note: couldn't import setuptools so using distutils instead.")
	from distutils.core import setup
import sys

setup (name = 'AppleScriptWrapper',
       packages = ['AppleScriptWrapper'],
       version = '0.5.6',
       license = 'Public Domain',
       description = 'Wrapper that makes AppleScripting on Python as easy, convenient, and extensible as possible',
       author = "Adam Ryan Morris",
       author_email = "amorris@mistermorris.com",
       url = "")
