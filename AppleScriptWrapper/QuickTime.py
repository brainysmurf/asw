from AppleScriptWrapper.Basic import AppleScriptWrapper

class Klass(AppleScriptWrapper):

    def __init__(self):
        AppleScriptWrapper.__init__(self, "QuickTime Player")

    def _default_target(self):
        return self.current_movie()

    def current_movie(self):
        return self.application.documents[0]

    def back_to_beginning(self):
        """
        Gets us back to the beginning of the movie, no matter how long
        """
        while not int(self.current_time()) == 0:
            self.step_backward(by=10000)

    def movie_finished(self):
        try:
            m = self.documents[0]()
        except:
            return True
        t = self.current_time()
        d = self.duration()
        return t >= d

    def full_screen(self):
        self.present()

    def close_without_saving(self):
        self.close(self.current_movie(), saving=self.k('no'))

if __name__ == "__main__":

    qt = QuickTime()
    qt.activate()
    qt.play()
    qt.present()
    qt.wait(times_longer=10)
    qt.stop()
    qt.back_to_beginning()
