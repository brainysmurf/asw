from AppleScriptWrapper.Basic import AppleScriptWrapper
import time


class Klass(AppleScriptWrapper):

    def __init__(self):
        AppleScriptWrapper.__init__(self, "iTunes")
        

if __name__ == "__main__":

    itunes = iTunesScripter()
    itunes.play()
    time.sleep(10)
    itunes.pause()
