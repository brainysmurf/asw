from AppleScriptWrapper.Basic import AppleScriptWrapper

class Klass(AppleScriptWrapper):
    def __init__(self):
        AppleScriptWrapper.__init__(self, "System Preferences")

    def change_panel(self, panel):
        self.application.current_pane.set(app.panes.ID('com.apple.preference.'+panel))

    def universal_access_panel(self):
        self.change_panel('universalaccess')

if __name__ == '__main__':

    sys = SystemPreferences()
    sys.universal_access_panel()
