from AppleScriptWrapper.Basic import AppleScriptWrapper
import re

class Klass(AppleScriptWrapper):

    def __init__(self):
        AppleScriptWrapper.__init__(self, "Firefox")

    def current_document(self):
        self.application.windows[0]

    def name_of_current_document(self):
        name = AppleScriptWrapper.name_of_current_document(self)
        if name:
            s = re.search(r'(.*)\.\w{3,} \(.*?\)', name)
            if s:
                return s.group(1)
            else:
                return name

    def extention_of_current_document(self):
        name = AppleScriptWrapper.name_of_current_document(self)
        if name:
            s = re.search(r'.*\.\w{3,4} \((\w{3,4}).*?\)', name)
            if s:
                return s.group(1)
            else:
                return self.default_extension

    def save(self):
        """ Nature of web browsing and Firefox makes this very tricky to solve """
        raise NotImplementedError

    def save_as(self, path):
        """ See save above """
        #self.save_gui(path)
        raise NotImplementedError

if __name__ == "__main__":

    f = Klass()
    print(f.save('/Users/brainysmurf/Desktop'))
