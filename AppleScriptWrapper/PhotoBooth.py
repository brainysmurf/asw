#!/usr/bin/env python3

from AppleScriptWrapper.Basic import AppleScriptWrapper

class Klass(AppleScriptWrapper):

    def __init__(self):
        AppleScriptWrapper.__init__(self, "Photo Booth")

    def photo_mode(self):
        self.command_down('3')

    def take_picture(self, wait_for_return=True):
        """
        Takes picture and knows how to wait for it to be ready again.
        Also handles it if it's already in some other mode
        """
        ref = self.menu_item_enabled('File', 'Take Photo')
        if not ref:
            self.photo_mode()
        self.command_down('t')
        if wait_for_return:
            self.wait_for_take_photo()

    def reveal_in_finder(self):
        self.command_down('r')

    def wait_for_take_photo(self):
        """
        Blocks until the Take Photo item of the File menu has been re-enabled
        Appropriate to call after taking a photo, as this is the built-in behavior
        Avoids infinite loop by not going past a half-minute.
        """
        ref = None
        self.start_timer()
        while not ref:
            ref = self.menu_item_enabled('File', 'Take Photo')
            if self.elapsed_time_since_start() > 0.5:
                ref = True
        self.stop_timer()

if __name__ == '__main__':

    p = Klass()
    p.take_picture()
