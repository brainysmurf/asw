from AppleScriptWrapper.Basic import AppleScriptWrapper
import os

class Klass(AppleScriptWrapper):
    def __init__(self):
        AppleScriptWrapper.__init__(self, 'TextEdit')

    def append(self, what):
        cur = self.current_document()
        cur.make(at=cur.text.end, new=self.k('word'), with_data=what)

    def save_as_pdf(self, path=None):
        if not path:
            self.save()
            path = self.current_document().path()
            path, name = os.path.split(path)
            name, ext  = os.path.splitext(name)
            
        self.click_menu_item('File', 'Save as PDF…')
        self.navigate_using_goto(path + name + 'pdf')


if __name__ == '__main__':

    te = Klass()
    te.save_as_pdf()
