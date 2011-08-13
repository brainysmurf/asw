"""
Fixes applescripting with Finder: can pass it paths, file objects, or any object with 'path' attribute, 
instead of what Applescript expects and is foreign to python: aliases

Works with classes or dictionaries
"""

from AppleScriptWrapper.Basic import AppleScriptWrapper
import mactypes
import os
import re
import collections

def movieoutput(s):
    print(s)

def reveal_in_finder(path):
    Klass().reveal(path)

def get_current_selections_in_finder():
    return Klass().paths_of_current_selections()

class Klass(AppleScriptWrapper):
    """
    Script the Finder using familar python types: path strings or file objects, or any object with a path attribute
    All methods that take a path argument are automatically handled so conversions are done automatically
    All methods, where appropriate, return a path string
    """
    def __init__(self):
        AppleScriptWrapper.__init__(self, "Finder")

    def current_selections(self, **kwargs):
        """
        Returns current item, including ability to specify resulttype
        """
        return self.selection.get(**kwargs)

    def ls(self, path):
        """
        Returns list of files at path; uses os module which is waaay faster than the finder
        """
        return os.path.listdir(path)
   
    def paths_of_current_selections(self):
        """
        Returns list in path format of current selections
        """
        return [item.path for item in self.current_selections(resulttype=self.k('alias'))]

    def reference_from_path(self, path):
        """
        Returns a Finder reference form ... not quite the same as alias reference form!
        """
        return self.application.items[mactypes.Alias(path)]

    def alias_from_whatever(self, whatever):
        """
        Takes any object whatsoever and returns an alias, which Applescript needs to work properly
        This way self can use file objects, written out paths, or any object with a path attribute
        """
        verbose = False
        verbose and output("Returning the following from alias_from_whatever:")
        if isinstance(whatever, file):
            verbose and output( "Alias(whatever.name)" )
            return mactypes.Alias(whatever.name)
        elif isinstance(whatever, mactypes.Alias):
            verbose and output("whatever")
            return whatever
        elif hasattr(whatever, 'path'):
            if isinstance(whatever.path, collections.Callable):
                verbose and output("Alias(whatever.path())")
                return mactypes.Alias(whatever.path())
            else:
                verbose and output("Alias(whatever.path)", whatever.path)
                return mactypes.Alias(whatever.path)
        elif not isinstance(whatever, str) and 'path' in whatever:
            verbose and output("whatever['path']", whatever['path'])
            return mactypes.Alias(whatever['path'])
        elif isinstance(whatever, list):
            # recurively derive list
            return [self.alias_from_whatever(item) for item in whatever]
        else:
            verbose and output("Alias(whatever)")
            return mactypes.Alias(whatever)

    def path_from_whatever(self, whatever):
        """ Reverse operation of alias_from_whatever """
        try:
            if os.path.exists(whatever):
                return whatever
        except TypeError:
            pass  # "cannot convert object to str implicitely" error
        if isinstance(whatever, file):
            return whatever.name
        elif isinstance(whatever, mactypes.Alias):
            return whatever.path
        elif hasattr(whatever, 'path'):
            if isinstance(whatever.path, collections.Callable):
                return whatever.path()
            else:
                return whatever.path
        elif 'path' in whatever:
            return whatever[path]
        else:
            return whatever

    def path_from_alias(self, alias):
        return alias.path

    def set_label_for_path(self, label, path):
        alias = self.alias_from_whatever(path)
        alias.label.set(label)

    # The following methods are not convenience functions but attempting to override Finder's need for files and/or aliases
    def open(self, f, using=None):
        """
        @using string of application to open
        """
        if using:
            self.application.open(self.alias_from_whatever(path), using=appscript.app(using))
        else:
            self.application.open(self.alias_from_whatever(path))

    def reveal(self, path):
        self.application.reveal(self.alias_from_whatever(path))

    def select(self, path):
        self.application.select([self.alias_from_whatever(p) for p in path])

    def spotlight_set_comment(self, path, comment):
        """
        Sets spotlight comment, use with care
        """
        ref = self.reference_from_path(path)
        ref.comment.set(comment)

    def spotlight_add_comment(self, path, comment, no_duplicates=True):
        """
        Makes a copy of comment, adds to it, at the front, and then sets
        Does not allow duplicates by default TODO: implement if False
        Adds return character
        """
        old_comment = self.spotlight_get_comment(path)
        if comment in old_comment:
            return
        if not comment:
            return
        old_comment += "\n"
        new_comment = old_comment + comment
        self.spotlight_set_comment(path, new_comment)
            
    def spotlight_get_comment(self, path):
        """
        Sets spotlight comment
        """
        return self.reference_from_path(path).comment()

    def spotlight_remove_comment(self, path, comment):
        """
        Removes comment by splitting
        Does not fail if comment is not already there
        """
        old_comment = self.spotlight_get_comment(path)
        if comment in old_comment:
            #TODO what if it follows a \n?
            new_comment = "".join(old_comment.split(comment))
            self.spotlight_set_comment(path, new_comment)

    def move(self, paths, to=None, to_idiom=None):
        """
        to_idiom ['trash']
        """
        if not to and not to_idiom:
            return  # raise error?
        
        if not isinstance(paths, list):
            paths = [path]
        else:
            paths = [self.reference_from_path(p) for p in paths]

        if not to_idiom and to:
            the_to = mactypes.Alias(to)
        elif to_idiom:
            the_to = getattr(self._app_ref, to_idiom.lower())

        self.application.move(paths, to=the_to)

    def rename(self, path, new_name):
        ref = self.reference_from_path(path)
        ref.name.set(new_name)

if __name__ == '__main__':

    f = Klass()

    finder = Klass()
    print(finder.reference_from_path('/tmp').comment())
