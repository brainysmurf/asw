"""
A pythonic wrapper over Applescript, with convenience in mind

Criteria:

  * Uses python conventions throughout
  * Don't have to worry about targeting the right object, just find the command you want and use it
  * 'x_x_convenience' methods available to make common operations more pythonic, for example display_dialog_convenience
  * Additional methods available to do common operations and are available for free to each created class
  * Fixes Applescript programming in that workarounds are taken care of in the classes themselves
  * activate() is called by default with each command, this can be turned of using "with self.context_no_activate():"

Caveat: Name collisions may exist, depending on use case: get around them by using self.application, self.standard_additions, or self.system_events

Dependencies: appscript

Use: 
   * from ApplescriptWrapper.name_of_app import Klass
   -or, to make your own-
   * from AppleScriptWrapper.Basic import AppleScriptWrapper
     class AppWrapper(AppleScriptWrapper):
          def __init__(self):
              AppleScriptWrapper.__init__(self, name_of_app)
"""

import appscript
from appscript.reference import CommandError
import osax
import copy
import time
import os
import glob
import collections

class User_Canceled(Exception): pass
class GUIScriptingNotEnabled(Exception): pass

def get_app(app_name):
    verbose = True
    try:
        a = __import__('AppleScriptWrapper.'+app_name, globals(), locals(), ['Klass'], -1).Klass()
        verbose and print("Found {} in AppleScriptWrapper package".format(app_name))
    except ImportError:
        print('hi')
        a = AppleScriptWrapper(app_name)
        verbose and print("Not found {} in AppleScriptWrapper package".format(app_name))
    return a

def get_front_app():
    """
    Return applescritable front app, escape will send it an escape key
    """
    return get_app(get_name_of_front_application())

def tell_app_to_do(app_name, command, *args, **kwargs):
    """
    Simple one-liner
    """
    return getattr(get_app(app_name), command)(*args, **kwargs)

def reveal_in_finder(what):
    """
    Can pass it anything, path or file object, or python object such as dictionary with object.path or object[path],
    or list containing therein, and reveals it in the finder
    """
    get_app("Finder").reveal(what)

def get_name_of_front_application():
    return appscript.app('System Events').processes[appscript.its.frontmost == True].processes[1].short_name()

def get_list_of_every_open_application():
    return [name for name in appscript.app('System Events').processes.short_name() if isinstance(name, str)]

def choose_from_list(llist, *args, **kwargs):
    return AppleScriptWrapper(get_name_of_front_application()).choose_from_list_convenience(llist, *args, **kwargs)

class App_Dictionary_Only(object):
    """
    Use this class if you know that you'll only need tell app statements
    """
    default_extension = ""

    def __init__(self, app_name):
        self.set_application(app_name)   # sets up reference
        self.auto_activate = True
        self.reset_auto_activate_on_exit = False
        self._rerouted_target = None
        self.reset_default_target_on_exit = False
        self._app_ref = appscript.app

    def __getattr__(self, name):
        """
        Old version
        """
        verbose = False
        if name == "default_target":
            if not self._rerouted_target:
                return self._default_target()
            else:
                if isinstance(self._rerouted_target, collections.Callable):
                    return self._rerouted_target()
                else:
                    return self._rerouted_target
        else:
            try:
                g = getattr(self.application, name)  # application-level
                if g:
                    try:
                        g()   # yuck
                    except Exception as e:
                        if str(e.args[2]) == "Command failed: Can't get reference. (-1728)":
                            verbose and print("sending on to default target")
                            raise AttributeError
                    if self.auto_activate:
                        self.activate()
                    verbose and print("getattr returning self.application.{0}".format(name))
                    return g
            except AttributeError as CommandError:
                g = getattr(self.default_target, name)  # target-level, usually 'front document'
                if g:
                    if self.auto_activate:
                        self.activate()
                    verbose and print("getattr returning self.default_target: {0}".format(g))
                    return g
        return None
    """

    def __getattr__(self, name):

        verbose = True
        if name == "default_target":
            if not self._rerouted_target:
                return self._default_target()
            else:
                if callable(self._rerouted_target):
                    return self._rerouted_target()
                else:
                    return self._rerouted_target
        else:
            try:
                g = getattr(self.default_target, name)
                if g:
                    if self.auto_activate:
                        self.activate()
                    verbose and print("getattr returning self.default_target: {}".format(g))
                    return g
            except AttributeError:
                g = getattr(self.application, name)
                if g:
                    if self.auto_activate:
                        self.activate()
                    verbose and print("getattr returning self.default_target: {}".format(g))
                    return g
        return None
    """
    
    def quit(self):
        self.application.quit()

    def activate(self):
        """ activates, brings to front """
        """ needed to define at this level to avoid recursion in getattr traffic """
        self.application.activate()

    def is_running(self):
        return self.isrunning()

    def set_application(self, app_name):
        self.app_name = app_name
        self.application = appscript.app(app_name)
       
    def get_app(self):
        return self.application

    def k(self, constant):
        """ Access to appscript k constants """
        return getattr(appscript.k, constant)

    def convert_options_to_list(self, dictionary):
        """ Convert dictionary to list of k constants, useful for convenience methods """
        return [self.k(key) for key in dictionary]

    def get_object(self, objekt):
        """ Access to appscript objects """
        return getattr(self.application, objekt)
        
    def _default_target(self):
        """ the front document """
        return self.current_document()
        
    def current_document(self):
        """
        Should return the 'frontmost' or 'front' ... I think 'current' is the best term 
        because if you're remotely controlling it it's not exactly 'front' anyway
        """
        return self.application.documents[0]

    def extension_of_current_document(self):
        return self.default_extension

    def name_of_current_document(self):
        """ Should be overriden if more processing is needed """
        try:
            return self.application.windows[0].name()
        except:
            return None

    #
    # Methods that have to do with selections
    #

    def text_of_selection(self):
        """ selection as text """
        try:
            return self.selection()(resulttype=self.k('text'))
        except AttributeError:
            # no applescriptable 'selection' copy and paste ... ugly
            # FIXME: What if the clipboard is empty?
            old = self.the_clipboard()
            self.command_down('c')
            new = self.the_clipboard()
            self.set_the_clipboard_to(None)
            return new
            

    # End of selection-type

    def context_no_activate(self):
        self.auto_activate = False
        self.reset_auto_activate_on_exit = True
        return self

    def context_target(self, target):
        """ target should be a lambda """
        self._rerouted_target = target
        self.reset_default_target_on_exit = True
        return self

    def context_selection(self):
        return self.context_target(self.selection)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.reset_auto_activate_on_exit:
            self.auto_activate = True
            self.reset_auto_activate_on_exit = False
        if self.reset_default_target_on_exit:
            self._rerouted_target = None
            self.reset_default_target_on_exit = False

class App_SystEvents_StndAdditions(App_Dictionary_Only):
    """
    Use this class to enable GUI scripting and standard additions
    """
    def __init__(self, *args, **kwargs):
        App_Dictionary_Only.__init__(self, *args, **kwargs)
        self.standard_additions = None
        self.system_events = None
        
    def __getattr__(self, name):
        """
        Routes attribute requests through app dictionary by default, then System Events dictionary, then Standard Additions
        Name collisions are not resolved, use internal objects explicity to resolve them
        """
        verbose = False
        try:
            return App_Dictionary_Only.__getattr__(self, name)
        except AttributeError:
            try:
                if not self.system_events:
                    self.system_events = appscript.app('System Events').processes[self.app_name]
                g = getattr(self.system_events, name)
                if g:
                    if self.auto_activate:
                        self.activate()  # GUI scripting requires app to be activated
                    verbose and print("Returning self.system_events.{0}".format(name))
                    return g
            except AttributeError:
                if not self.standard_additions:
                    self.standard_additions = osax.OSAX(name=self.app_name)  # launches an osax, very slow, egro we make it dynamic ... and last
                try:
                    g = getattr(self.standard_additions, name)
                    if g:
                        if self.auto_activate:
                            self.activate()
                        verbose and print("Returning self.standard_additions.{0}".format(name))
                        return g
                except AttributeError:
                    raise AttributeError("Unknown attribute!")

class AppleScriptWrapper(App_SystEvents_StndAdditions):

    def __init__(self, name):
        App_SystEvents_StndAdditions.__init__(self, name)
        self._wait = 0.25
        
    def get_list_of_documents(self):
        return self.application.documents[:]

    def file_is_open(self, title):
        return title in [f.name() for f in self.get_list_of_documents()]

#    def close(self):
#        print self.current_document()
#        self.application.close(self.current_document())

    def close_without_saving(self):
        self.application.close(self.current_document(), saving=self.k('no'))

    def save(self):
        self.application.save(self.current_document())

    def save_as(self, path):
        self.application.save(self.current_document(), in_=path)

    def save_as_pdf(self, path=None):
        """
        Automates the print as pdf function in print dialog box, takes current document and saves it as its name + 'pdf'
        Saves it first for new documents when path is not specified
        """
        if not path:
            path = self.current_document().path()
            if not path:
                self.save()
                path = self.current_document().path()
            path, name = os.path.split(path)
            name, ext  = os.path.splitext(name)
            path = path + name + ext
        try:
            self.application.save(self.current_document(), in_=path, as_='pdf')
        except:
            self.application.save(self.current_document(), in_=path + '.pdf')

    def save_gui(self, path, confirm=True):
        """ 
        Saves current document using gui scripting, if confirm is false then lets user check and hit return 
        
        """
        self.command_down('s')
        path = self.resolve_name_collision(path)
        self.navigate_using_goto(path, confirm=confirm)

    def navigate_using_goto(self, path, confirm=False):
        self.command_down('G')
        self.keystroke(path)
        self.keystroke_return()
        if confirm:
            self.keystroke_return()

    def wait(self, times_longer=1):
        time.sleep(self._wait * times_longer)

    def menu_item_present(self, menu, item):
        """ Returns menu item object if exists, false if not, can be used to see if present """
        ref = self.menu_bars[1].menu_bar_items[menu].menus[menu].menu_items[item]
        try:
            ref = ref()
        except:
            ref = False
        return ref

    def submenu_item_present(self, menu, submenu, item):
        ref = self.menu_bars[1].menu_bar_items[menu].menus[menu].menu_items[submenu].menus[submenu].menu_items[item]
        try:
            ref = ref()
        except:
            ref = False
        return ref

    def menu_item_enabled(self, menu, item):
        ref = self.menu_item_present(menu, item)
        if not ref: return False
        return ref.enabled()

    def submenu_item_enabled(self, menu, submenu, item):
        ref = self.submenu_item_present(menu, submenu, item)
        if not ref: raise Exception("Passed invalid menu and item to menu_item_enabled")
        return ref.enabled()            

    def click_menu_item(self, menu, item):
        ref = self.menu_item_present(menu, item)
        if ref:
            self.wait()
            ref.click()
            self.wait()   

    def click_submenu_item(self, menu, submenu, item):
        ref = self.submenu_item_present(menu, submenu, item)
        if ref:
            self.wait()
            ref.click()
            self.wait()

    def toggle_menu_item(self, menu, item):
        ref = self.menu_item_present(menu, item)
        if ref:
            self.wait()
            ref.click()
            self.wait()

    def toggle_submenu_item(self, menu, submenu, item):
        ref = self.submenu_item_present(menu, submenu, item)
        if ref:
            self.wait()
            ref.click()
            self.wait()

    def menu_item_checked(self, menu, item):
        return self.menu_item_present(menu, item).selected()

    def keystroke_convenience(self, key, times=1, **keysdown):
        """ convenience method for all keystrokes with **keysdown passed as named options """
        self.wait()
        options = self.convert_options_to_list(keysdown)
        for i in range(0, times):
            if options:
                self.keystroke(key, using=options)
            else:
                self.keystroke(key)
        self.wait()

    def check_menu_item(self, menu, item, boolean):
        self.menu_item_present(menu, item).selected.set(boolean)      

    def keystroke_return(self):
        self.keystroke_convenience('\r')

    def command_down(self, char):
        """ convenenience method for keystroke with command down """
        self.keystroke_convenience(char, command_down=True)
    
    def paste(self):
        self.command_down('v')

    def option_down(self, char):
        self.keystroke_convenience(char, option_down=True)

    def command_option_down(self, char):
        """ convenenience method for keystroke with command down """
        self.keystroke_convenience(char, command_down=True, option_down=True)

    def keystroke_idiom(self, idiom, **keysdown):
        options = self.convert_options_to_list(keysdown)
        possible_idioms = {'escape': 53, 'down arrow':125, 'up arrow':126, 'left arrow': 123, 'right arrow':124}
        try:
            this_idiom = possible_idioms[idiom.lower()]
        except:
            return  # no error
        self.wait()
        if options:
            self.key_code(this_idiom, using=options)
        else:
            self.key_code(this_idiom)

    def display_alert_convenience(self, prompt, message, as_="warning", **kwargs):
        possible_alert_kinds = {'warning':self.k('warning')}
        self.display_alert(prompt, message=message, as_=possible_alert_kinds[as_])

    def display_dialog_convenience(self, prompt, default_answer=None, buttons=['Cancel', 'OK'], default_button=0, timeout=10000, 
                                   cancel_button_name="Cancel", **kwargs):
        """ returns text if default_answer or the text of the button if not, throws exception if Cancel is pushed """

        def pushed_cancel_button(_response):
            if _response is None: return True
            return buttons.index(_response[self.k('button_returned')]) == 0 and buttons[0] == cancel_button_name

        if not default_button:
            default_button = len(buttons)
        if default_answer is None:
            response = self.display_dialog(prompt,
                                           buttons=buttons, default_button=default_button,
                                           timeout=timeout, **kwargs)
            if pushed_cancel_button(response):
                raise User_Canceled
            return response[self.k('button_returned')]
        else:
            response = self.display_dialog(prompt, default_answer=default_answer,
                                           buttons=buttons, default_button=default_button,
                                           timeout=timeout, **kwargs)
            if pushed_cancel_button(response):
                raise User_Canceled
            return response[self.k('text_returned')]            

    def get_int_input(self, prompt, default_answer="1", buttons=['Cancel', 'OK'],
                      default_button=2, minimum=0, maximum=10000):
        num = minimum - 1
        while not (minimum <= num <= maximum):
            reply = self.get_input(prompt, default_answer=default_answer, buttons=buttons, default_button=default_button)
            try:
                num = int(reply)
            except:
                num = minimum - 1
        return num

    def get_input_loop(self):
        """ forget what this was for exactly """
        raise NotImplemented

    def get_input_loop_i(self):
        raise NotImplemented    

    def choose_from_list_convenience(self, prompt, llist, timeout=10000, **kwargs):
        """ returns string or list of string of item chosen in llist, raises UserCanceled if Cancel is pressed """
        response = self.choose_from_list(llist, with_prompt=prompt, timeout=timeout, **kwargs)
        if response is None:
            raise Exception("Got strange return from choose_from_list")
        if response is False:
            raise User_Canceled
        if len(response) == 1:
            return response[0]
        else:
            return response

    def choose_file_convenience(self, prompt, file_types, **kwargs):
        """ will take list of dot notated file types """
        if not isinstance(file_types, list): file_types = [file_types]
        file_types = [f.lstrip('.') for f in file_types]
        return self.choose_file(with_prompt=prompt, of_type=file_types, **kwargs)

    def tell_app_to_do(self, app, do, *args, **kwargs):
        """
        Depreciated, should use module-level method instead
        """
        f = getattr(appscript.app(app), do)
        f(*args, **kwargs)

    def ensure_gui_scripting_activated(self, app_name="This application"):
        """
        Interact with user in a way that ensures GUI scripting is possible
        """

        def enabled():
            return app("System Events").UI_elements_enabled()

        if not enabled:
            from .SystemPreferences import SystemPreferences
            sys = SystemPreferences()
            sys.activate()
            sys.universal_acess_panel()
            sys.get_input("{0} utilizes the built-in Graphic User Interface Scripting ararchitecture of Mac OS X which is currently disabled\n\nYou can activate GUI Scripting by selecting the checkbox \"Enable access for assistive devices\" in the Universal Access preference pane, which will be visible once you click OK.".format(app_name),
                          buttons=["OK"])
            sys.activate()
            with self.context_no_activate():
                self.display_alert_convenience("Click OK when you have enabled access for assistive devices in the Universal Access preference pane", "")
        enabled = app("System Events").UI_elements_enabled()
        if not enabled:
            self.display_alert_convenience("you haven't enabled access for assistive devices.", "{} is quitting now.".format(app_name))
            raise GUIScriptingNotEnabled

    def start_timer(self):
        self._start_time = time.time()
        
    def stop_timer(self):
        self._start_time = 0
        
    def elapsed_time_since_start(self):
        """ returns in minutes the period of time taken """
        if not self._start_time: return 0
        return (time.time() - self._start_time) / 60

    def do_shell_script_convenience(self, command, authenticate=False, async=False, **kwargs):
        """ authenticate and asyncs are possible """
        if authenticate:
            sa = osax.OSAX()  # new instance needed
            sa.activate()
            result = sa.do_shell_script(command, administrator_privileges=True, **kwargs)
            self.activate()
            return result
        else:
            import subprocess
            p = suprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
            if not async:
                return p.communicate()
            else:
                return p

    def do_in_thread(self, do, *args, **kwargs):
        import threading
        t = threading.Thread(target=do, *args, **kwargs)
        t.start()
        return t

    def resolve_name_collision(self, path):
        """
        Return a file path that of a file that does not already exist
        """
        _path, _file_name = os.path.split(path)
        _file, _ext  = os.path.splitext(_file_name)
        if _file_name in os.listdir(_path):
            files_already = glob.glob("{1}-*{2}".format(_path, _file, _ext))
            if len(files_already) == 1:
                return "{0}/{1}-1{2}".format(_path, _file, _ext)
            else:
                start = len(_file)
                duplicates = [os.path.splitext(f)[0] for f in files_already if os.path.splitext(f)[0][start+1:].isdigit()]
                last_int = duplicates[-1][start+1:]
                return "{0}/{1}-{2}{3}".format(_path, _file, int(last_int) + 1, _ext)
        else:
            return path
            
if __name__ == "__main__":

#    reveal_in_finder(['/Users/brainysmurf', '/Applescripts'])
#    a = AppleScriptWrapper('TextEdit')
#    print a.frontmost()
#    print get_name_of_front_application()

    f = get_name_of_front_application()
    print(f)

