from AppleScriptWrapper.Basic import AppleScriptWrapper

class Klass(AppleScriptWrapper):
    def __init__(self):
        AppleScriptWrapper.__init__(self, 'Safari')
