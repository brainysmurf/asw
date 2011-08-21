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

class MoodleSupport:
    glossary = """
    <GLOSSARY>
      <INFO>
        <NAME>{}</NAME>
        <INTRO> {} </INTRO>
        <ALLOWDUPLICATEDENTRIES>0</ALLOWDUPLICATEDENTRIES>
        <DISPLAYFORMAT>dictionary</DISPLAYFORMAT>
        <SHOWSPECIAL>1</SHOWSPECIAL>
        <SHOWALPHABET>1</SHOWALPHABET>
        <SHOWALL>1</SHOWALL>
        <ALLOWCOMMENTS>1</ALLOWCOMMENTS>
        <USEDYNALINK>1</USEDYNALINK>
        <DEFAULTAPPROVAL>1</DEFAULTAPPROVAL>
        <GLOBALGLOSSARY>0</GLOBALGLOSSARY>
        <ENTBYPAGE>10</ENTBYPAGE>
        <ENTRIES>
    {}
        </ENTRIES>
      </INFO>
    </GLOSSARY>
    """

    entry_format = """
          <ENTRY>
            <CONCEPT>{}</CONCEPT>
            <DEFINITION>{}.&lt;br /&gt;&lt;br /&gt;&lt;img width=&quot;{}&quot; vspace=&quot;0&quot; hspace=&quot;0&quot; height=&quot;{}&quot; border=&quot;0&quot; src=&quot;{}&quot; alt=&quot;{}&quot; title=&quot;{}&quot; /&gt;&lt;br /&gt; </DEFINITION>
            <FORMAT>1</FORMAT>
            <USEDYNALINK>0</USEDYNALINK>
            <CASESENSITIVE>0</CASESENSITIVE>
            <FULLMATCH>0</FULLMATCH>
            <TEACHERENTRY>1</TEACHERENTRY>
          </ENTRY>
    """

class Glossary(MoodleSupport):
    """
    Class that builds a glossary format
    Does it the ugly way by just using text formatted in an xml format
    """

    def __init__(self, name, intro):
        self.define_headers(name, intro)
        self._entries = []

    def define_headers(self, name, intro):
        self._headers = self.glossary.format(name, intro, "{}")  # keep last one for entries
        
    def add_entry(self, concept, definition, width, height, src, alt, title):
        """
        Call this to build list of ideas
        """
        self._entries.append(self.entry_format.format(concept, definition, width, height, src, alt, title))

    def result(self):
        """ Format everything """
        return self._headers.format("\n".join(self._entries))


class Klass(AppleScriptWrapper):
    """
    Script ProVoc
    """
    def __init__(self):
        AppleScriptWrapper.__init__(self, "ProVoc")

    def export(self):
        """
        Translates that basic export command to a more pythonic version
        """
        data = self.application.export()
        return [d.split('\t') for d in data.split('\n') if d]

    def export_for_moodle(self):
        """
        Puts it into xml format good for moodle
        """
        glossary = Glossary("Testing", "Intro")
        data = self.export()
        for item in data:
            glossary.add_entry(item[0], item[1], "", "", item[2], item[0], item[0])
        return glossary.result()

    def saved(self):
        if not self.path_of_document():
            return False
        else:
            return True

    def path_of_document(self):
        return self.path()

if __name__ == '__main__':

    provoc = Klass()
    with open('/tmp/provoctest.xml', 'w') as f:
        f.write(provoc.export_for_moodle())
