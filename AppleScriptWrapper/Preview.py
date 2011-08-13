from AppleScriptWrapper.Basic import AppleScriptWrapper

class Klass(AppleScriptWrapper):

    def __init__(self):
        AppleScriptWrapper.__init__(self, "Preview")

    def zoom(self):
        self.click_menu_item('Window', 'Zoom')
        for i in range(1, 2):
            self.command('+')

    def close(self):
        self.keystroke('w', command_down=True)


if __name__ == '__main__':


    p = Preview()
    p.zoom()
    p.wait(times_longer=5)
    p.close()
