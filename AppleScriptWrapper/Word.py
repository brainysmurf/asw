from AppleScriptWrapper.Basic import AppleScriptWrapper

class Klass(AppleScriptWrapper):
    def __init__(self):
        s = "hi"
        AppleScriptWrapper.__init__(self, "Microsoft Word")

    def text_of_selection(self):
        return self.application.selection.content()
