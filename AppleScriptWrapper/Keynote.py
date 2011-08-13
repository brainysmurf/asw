#!/usr/bin/env python

# I use _surrounding_underscores_ to denote primitive types

from AppleScriptWrapper.Basic import AppleScriptWrapper
import re

class CalledFunctionAssumingPlayModeButNotPlaying(Exception): pass
class CalledFunctionAssumingNotPlayModeButPlaying(Exception): pass

def output(s):
    print(s)

def convenience(statement, *args, **kwargs):
    """
    Send it a string of what you want it to.
    """
    a = Klass()
    return getattr(a, statement)(*args, **kwargs)

class Klass(AppleScriptWrapper):
    """
    Control Keynote with applescript
    """
    default_extension = ".key"
    
    def __init__(self, slideshow_number=None):
        """
        Sets up Keynote so that it uses whichever slideshow throughout
        """
        AppleScriptWrapper.__init__(self, "Keynote")
        if not slideshow_number:
            slideshow_number = 1

        self._edit = []
        """
        The following line shouldn't be there because it uses system_events, but it's assumed
        """
        #self.save_gui_state()

    # Keynote calls documents slideshows, so override default behaviour to reflect
    def _default_target(self):
        return self.current_slide()

    def current_slideshow(self):
        return self.application.slideshows[0]

    def current_slide(self):
        return self.current_slideshow().current_slide
            
    # Following commands are ease-of-use sorts

    def get_listpath_of_current_slideshow(self):
        """
        Returns the path as a list
        """
        return self.path().split('/')

    def count_of_slides_in_slideshow(self, slideshow):
        return self.get_app().slideshows[slideshow].count(each=k.slide)

    def count_of_slides_in_current_slideshow(self):
        return self.current_slideshow().count(each=k.slide)

    def derive_num_from_slide_ref(self, slideref):
        which = str(slideref)
        where = re.findall(r'\[([0-9]+)\]', which)
        if not where:
            output("Warning, could not get slide number")
        return int(where[0])

    def current_slide_num(self):
        return self.derive_num_from_slide_ref(self.current_slide())

    def get_slide_reference(self, slide_number):
        return self.application.slideshows.slides[slide_number]

    # Following commands are direct translations of basic applescript abilities, and their close -- slightly abstracting -- cousins

    def get_titleorbody_of_current_slide(self, property):
        attr = getattr(self.current_slide(), property, None)
        if attr:
            return attr().strip()
        else:
            output("Warning, could not get", property, "of the current slide")
            return ""

    def get_title_of_current_slide(self):
        return self.get_titleorbody_of_current_slide('title')

    def get_body_of_current_slide(self):
        return self.get_titleorbody_of_current_slide('body')

    def get_titleorbody_of_slide(self, _property_, slide_number):
        attr = getattr(self.get_slide_reference(slide_number), _property_, None)
        if attr:
            return attr()[0].strip()
        else:
            output("Warning, could not get", property, "of slide", slide_number)
            return ""

    def get_body_of_slide(self, slide_number):
        return self.get_titleorbody_of_slide("body", slide_number)

    def get_title_of_slide(self, slide_number):
        return self.get_titleorbody_of_slide("title", slide_number)

    def set_titleorbody_of_slide(self, _property_, slide_number, _new_):
        """
        If keynote is not in editing mode, will put request into self._edit_when_can
        Works in tandem with self.can_edit_now() which is called when stop_slideshow is called
        """
        if self.playing():
            self._edit.append( (_property_, slide_number, _new_) )
            
        else:
            if _property_ not in ["title", "body"]:
                raise Exception("Passed {0} crap to set_titleorbody_of_slide".format(str(_property_)))
            reference = getattr(self.get_slide_reference(slide_number), _property_)
            reference.set(_new_)

    def do_edits_now(self):
        if self._edit:
            for request in self._edit:
                property, slide_num, s = request
                self.set_titleorbody_of_slide(property, slide_num, s)
            self._edit = []

    def set_title_of_slide(self, slide_number, _new_title_):
        """ See above """
        self.set_titleorbody_of_slide("title", slide_number, _new_title_)

    def blank_title_of_slide(self, slide_number):
        """ See above """
        self.set_titleorbody_of_slide("title", _slide_number, "")

    def set_body_of_slide(self, slide_number, _new_title_):
        """ See above """
        self.set_titleorbody_of_slide("body", slide_number, _new_title_)

    def blank_body_of_slide(self, slide_number):
        self.set_titleorbody_of_slide("body", slide_number, " ")

    def start(self):
        self.application.start()

    def start_from_slide(self, slide_number):
        """
        Starts presentation from slide number
        Prevents applescript error by checking to see that I'm playing first
        """
        self.application.start_from(self.get_slide_reference(slide_number))

    def advance(self):
        self.get_app().advance()

    def stop_slideshow(self):
        self.get_app().stop_slideshow()
        self.do_edits_now()

    def jump_to_slide(self, slide_number):
        """
        Jumps to slide, without transitions
        """
        self.application.jump_to(self.get_slide_reference(slide_number))

    def show_slide(self, slide_number):
        """ Alias for above """
        self.jump_to_slide(slide_number)

    def add_chart(self, slide_number, row_names=[], column_names=[], data=[], type="horizontal_bar_3d", group_by="column"):
        """
        What a horrible abstraction ... no error checks!!
        One benefit I would get from checking is that I don't have to delete the legend every ferking time
        """
        self.get_slide_reference(slide_number).add_chart(row_names=row_names, column_names=column_names, data=data, type=type, group_by=group_by)
        self.wait()
        self.keystroke("D", command_down=True)

    def add_horizontal_bar_3d_chart(self, slide_number, **kwargs):
        """ See above """
        self.add_chart(slide_number, 
                       type="horizontal_bar_3d", 
                       **kwargs)

    def add_line_2d_chart(self, slide_number, **kwargs):
        self.add_chart(slide_number,
                       type="line_2d",
                       **kwargs)

    def playing_and_frontmost(self):
        return self.playing() and self.frontmost()

    def is_frozen(self):
        return self.get_app().frozen()

    def is_playing(self):
        return self.application.playing()

    def move_slide(self, this_slideshow, this_slide_num, to_slideshow, to_num):
        """
        Move the slide defined at this_slide so that it is now the slide defined by to_ parameters
        0 is at the beginning
        > count of slides is at the end
        """
        to_where = self.get_app().slideshows[to_slideshow]
        if to_num <= 1:
            to_where = to_where.slides[1].before
        elif to_num > self.count_of_slides_in_slideshow(to_slideshow):
            to_where = to_where.slides[-1].after
        else:
            to_where = to_where.slides[to_num-1].after
        self.get_app().slideshows[this_slideshow].slides[this_slide_num].move(to=to_where)

    def import_foreign_slide(self, foreign_slideshow, foreign_slide_num):
        """
        Takes a slide specified in slide_num and slideshow_name and puts it so that it appears wherever we are in the slideshow
        """
        ____verbose = False

        current_slideshow = self.name()
        current_where = self.current_slide_num()

        self.move_slide(foreign_slideshow, foreign_slide_num, current_slideshow, current_where)

    # These are useful functions

    def do_this_while_playing_that_when_not(self, this, that, this_messages=None, that_messages=None):
        """
        Repeatedly calls this and that (generator functions) until keynote stops runnning
        Intended to be a script that runs as long as Keynote is open to act as a "piggyback app"
        "this" and "that" can toggle between play states easily
        Not the best implementation but the benefits are huge (to a teacher/lecturer certainly).
        The function can return a dictionary to send messages, stopped when it "falls off" or returned
        Can optionally use message handlers for any further processing
        """

        ____verbose = False
        ____verbose and output('Inside do_this_while_playing_that_when_not with arguments: this:{0}, that:{1}, this_messages:{2}, that_messages:{3}'.format(this, that, this_messages, that_messages))

        while self.is_running():

            try:
                self.wait()
                for i in this():
                    if this_messages and i:
                        i['play_state'] = self.playing()
                        this_messages(i)
                for i in that():
                    if that_messages and i:
                        i['play_state'] = self.playing()
                        that_messages(i)

            except CalledFunctionAssumingPlayModeButNotPlaying as err:
                output("Exception CalledFunctionAssumingPlayModeButNotPlaying raised with message: {0}".format(err.args))

    def detect_slide_change(self):
        """
        Returns a dictionary {'advanced':ref} where ref is a reference to the slide that was advanced to
        """
        ____verbose = True

        current_slide = self.current_slide()
        play_state = self.playing()

        ____verbose and output('Entered detect_slide_change and current_slide is {0}, and play state is {1}'.format(current_slide, play_state))

        while self.playing_and_frontmost():
            ____verbose and output('Inside the loop while self.playing_and_frontmost')
            self.wait()
            new_current_slide = self.current_slide()
            if new_current_slide != current_slide: 
                ____verbose and output('Decided that we have come across a new page')
                old_slide = current_slide
                current_slide = new_current_slide
                page_difference = self.derive_num_from_slide_ref(new_current_slide) - self.derive_num_from_slide_ref(old_slide)
                ____verbose and output('About to yield the following -- change: {0}, slide_ref: {1}'.format(page_difference, current_slide))
                yield {'change':page_difference,
                       'slide_ref':current_slide}
            else: yield {}
        if play_state != self.playing():
            ____verbose and output('Decided that the play stage has changed and about to yield play_state: False')
            yield {'play_state_changed':False}

    def detect_play_or_edit(self):
        ____verbose = False
        
        play_state = self.playing()
        slide_num = self.current_slide_num()
        slide_title, slide_body = self.get_title_of_slide(slide_num), self.get_body_of_slide(slide_num)

        while not self.playing_and_frontmost():
            ____verbose and output('Inside detect_play\' loop, with the following items:\nplay state is {0}\nslide num is {1}\nslide title is {2}\nslide body is {3}'.format(play_state, slide_num, slide_title, slide_body))
            self.wait()
            messages = {}

            if self.current_slide_num() == slide_num: 
                modified = (self.get_title_of_slide(slide_num) != slide_title) or (self.get_body_of_slide(slide_num) != slide_body)
                if modified:
                    messages['modified'] = True
                    messages['slide_ref'] = self.current_slide()
                    ____verbose and output('Decided that the user has MODIFIED the slide')
                    slide_title, slide_body = self.get_title_of_slide(slide_num), self.get_body_of_slide(slide_num)
                else:
                    ____verbose and output('Decided that the user has NOT modified the slide')
            else:
                ____verbose and output('Decided that the user has simply changed slides, update state and that is it')
                slide_num = self.current_slide_num()
                slide_title, slide_body = self.get_title_of_slide(slide_num), self.get_body_of_slide(slide_num)

            ____verbose and output('About to yield this: {0}'.format(messages))
            yield messages

        if play_state != self.playing():
            messages = {}
            messages['slide_ref'] = self.current_slide()
            messages['play_state_changed'] = True
            ____verbose and print('Decided that the play state has changed and about to yield this: {0}'.format(messages))
            yield messages

    def save_gui_state(self):
        """
        Puts in self._gui the details of how the user has set up his or her gui, for ease in going back and forth between states
        """
        self._gui = {}
        self._gui['show presenter notes'] = True if self.menu_item_present("View", "Show Presenter Notes") else False
        self._gui['show navigator'] = True if self.menu_item_present('View', "Navigator") else False

    def restore_gui_state(self):
        """
        Reads from self._gui and sets it back in place
        """
        if self._gui['show presenter notes']:
            self.click_menu_item("View", "Show Presenter Notes")
        if self._gui['show navigator'] and not self.menu_item_enabled("View", "Navigator"):
            self.click_menu_item("View", "Navigator")

    def make_comment(self):
        self.click_menu_item('Insert', 'Comment')

    def __del__(self):
        if hasattr(self, '_gui'):
            self.restore_gui_state()

if __name__ == '__main__':

    keynote = Klass()
    keynote.wait()
    for message in keynote.detect_play_or_edit():
        print(message)
