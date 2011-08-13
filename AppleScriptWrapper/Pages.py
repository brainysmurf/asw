#! /usr/local/bin/python

from AppleScriptWrapper.Basic import AppleScriptWrapper
import re

class ForEachSelection(object):
    """
    Iterator that returns the text of selection
    """
    def __init__(self, pages):
        self.pages = pages

    def __iter__(self):
        self.pages.capture_selection()
        return self

    def __next__(self):
        if self.pages._n >= len(self.pages._selection):
            raise StopIteration
        self.pages.select_using(self.pages._n)
        self.pages.next_selection()
        return self.pages.text_of_selection()

class Klass(AppleScriptWrapper):
    default_extension = ".pages"

    def __init__(self):
        AppleScriptWrapper.__init__(self, "Pages")
        self._selection = None

    def cycle_through_selections(self):
        return ForEachSelection(self)
    
    def get_selection(self):
        return self.selection()
   
    def set_selection(self, value):
        self.selection.set(value)

    def text_of_selection(self):
        return self.selection()(resulttype=self.k('text'))

    def append(self, what):
        cur = self.current_document()
        cur.make(at=cur.body_text.end, new=self.k('word'), with_data=what)

    def surrounding_text_of_selection(self, offset=40):
        sel = self.selection()
        if isinstance(sel, list):
            return ""
        start, end = self.start_end_of_selection(sel)
        start      = start - offset if start - offset >= 0 else 0
        count      = self.count_of_body_text()
        end        = end   + offset if end + offset < count else count
        return self.build_selection(start, end)(resulttype=self.k('text'))
        
    def build_selection(self, start, end):
        """ assumes front document """
        doc = self.current_document()  # does this work with targeting system in place?
        return doc.body_text.text[self.documents.body_text.characters[start]:doc.body_text.characters[end]]
        
    def start_end_of_selection(self, sel):
        results = re.findall(r'body_text\.characters\[(\d{1,})\]', str(sel))
        return [int(d) for d in results]

    # Selection state routines
    def capture_selection(self):
        """
        Store state of current selection
        """
        self._selection = self.get_selection()
        self._n = 0

    def selection_is_contiguous_block(self):
        if not self._selection:
            self.capture_selection()
        return not isinstance(self._selection, list)

    def select_using(self, n):
        """
        select the nth item in captured selection
        """ 
        self.select(self._selection[n])

    def change_selection_and_adjust(self, value):
        old = self.text_of_selection()
        if len(old) == len(value):
            # string length is equal so therefore no adjustments needed
            self.set_selection(value)
        else:
            # need to calculate offset value
            offset = len(value) - len(old)
            self.set_selection(value)
            new_selection = self._selection[:]
            for o in range(self._n, len(new_selection)):
                ref = new_selection[o]
                locations = re.findall(r"\[([0-9]+)\]", str(ref))
                first, last = locations
                first = int(first) + offset
                last = int(last) + offset
                docID     = re.search(r"documents\.ID\(([0-9]+)\)", str(ref)).group(1)
                docID = int(docID)
                new_selection[o] = self.application.documents.ID(docID).body_text.text[app.documents.ID(docID).body_text.characters[first]:app.documents.ID(docID).body_text.characters[last]]  # pack it up
            self._selection = new_selection

    def select_next(self):
        self.next_selection()
        if self._n < len(self._selection):
            self.select_using(self._n)
        else:
            self.select(None)

    def next_selection(self):
        self._n += 1

    def len_selection(self):
        return len(self._selection)
    
    def count_of_body_text(self):
        return self.documents[0].body_text.count(each=self.k('character'))
        
if __name__ == "__main__":
    
    pages = Klass()
    pages.append('HI')
