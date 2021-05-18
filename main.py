from logging import root
from kivy import Config
Config.set('graphics', 'fullscreen', 'Auto')
Config.set('graphics', 'resizable', False)
Config.set('kivy', 'exit_on_escape', '0')

# Config.set('graphics', 'position', 'custom')
# Config.set('graphics', 'left', 500)
# Config.set('graphics', 'top', 100)

# Config.set('graphics', 'resizable', False)
# Config.set('graphics', 'minimum_width', '900')
# Config.set('graphics', 'minimum_height', '700')
# Config.set('graphics', 'maximum_width', '900')
# Config.set('graphics', 'maximum_height', '700')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
# from kivy import utils
from kivy.uix import effectwidget as ew
import time
import threading

from kivy.clock import Clock, mainthread

from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
import os
from random_prompt_generator import random_prompt



# TODO Remove unused imports


Window.size = (900, 700)

writing_timer_on = False
writing_fs_timer_on = False
timer_force_stop = False
prompt = ''
got_prompt = False

class HomeScreen(Screen):
    def get_random_prompt(self,scrn):
        global got_prompt 
        global prompt

        def get_prompt():
            global got_prompt
            got_prompt = False
            scrn.ids["prompt_text"].text = ''
            try:
                prompt = random_prompt(2)
            except Exception:
                print('failed to get prompt')
                scrn.ids["prompt_text"].text = "Something went wrong"
            got_prompt = True
            scrn.ids["prompt_text"].text = prompt

        def run_progress_bar():
            global got_prompt
            indicator_value = 0
            scrn.ids["circular_bar_1"].pos = (450,320)
            while got_prompt == False:
                time.sleep(0.1)
                if indicator_value > 10:
                    indicator_value = 0
                scrn.ids["circular_bar_1"].value = indicator_value
                indicator_value += 1
            scrn.ids["circular_bar_1"].pos = (1000, 1000)
            scrn.ids["circular_bar_1"].value = 0
            
            

        get_prompt_thread = threading.Thread(target=get_prompt)
        run_progress_bar_thread = threading.Thread(target=run_progress_bar)
        get_prompt_thread.start()
        run_progress_bar_thread.start()
       
        # scrn.ids["prompt_text"].text = prompt

class WritingScreen(Screen):
    save = ObjectProperty(None)

    def full_screen(self):
        Window.fullscreen = 'auto'
        Window.maximize()
                
    def normal_screen(self):
        Window.fullscreen = False
        Window.size = (900, 700)  
    
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save what you wrote", content=content,
                            size_hint=(0.5, 0.5))
        self._popup.open()

    def save(self, path, filename):
        if '.txt' not in filename:
            filename = filename + '.txt'
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_i.text)
        self.dismiss_popup()
        # TypeOrDie.typing_timer(self=self, scrn=self,full_screen=False)

class WritingFullScreen(Screen):
    def exit_full_screen(self):
        Window.fullscreen = False
        Window.size = (900, 700)
    
        
class WindowManager(ScreenManager):
    pass

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


kv = Builder.load_file('kivy-interface.kv')


class TypeOrDie(App):

    def build(self):
        Window.clearcolor = (32/255.0, 31/255.0, 29/255.0, 1)
        return kv

    def timer_manual_stop(self):
        global timer_force_stop
        timer_force_stop = True

    def typing_timer(self, scrn, full_screen):

        @mainthread  # this is needed because openGL has issues with multiple threads so we force the blur_text function to run on the main thread
        def blur_text(blur_size):
            scrn.ids["blur_effect"].effects = {ew.HorizontalBlurEffect(size=blur_size)}
            scrn.ids["text_input"].focus = True

        def run_timer():
            global writing_timer_on
            global writing_fs_timer_on
            global timer_force_stop
            timer_force_stop = False
            switch_screens = False

            # scrn.blur_text(0)
            blur_text(0)

            if full_screen == False:    
                writing_timer_on = True
                writing_fs_timer_on = False
            else:
                writing_timer_on = False
                writing_fs_timer_on = True
            
            max_idle_period = 10
            current_idle_period = 0
            current_text = scrn.text_i.text
            while current_idle_period < max_idle_period:
                if timer_force_stop == True:
                    print ('Timer stopped manually')
                    writing_fs_timer_on = False
                    writing_timer_on = False
                    break
                if full_screen == False:
                    if writing_timer_on == False:
                        print('stopping normal screen timer due to switching to full screen')
                        switch_screens = True
                        break
                else:
                    if writing_fs_timer_on == False:
                        print('stopping full screen timer due to switching to normal screen')
                        switch_screens = True
                        break
                time.sleep(1)
                if current_text == scrn.text_i.text:
                    current_idle_period += 1
                    scrn.ids["circular_bar"].value =  current_idle_period
                    # print(f'progress bar position {scrn.ids["circular_bar"].pos}')
                    # print(
                    #     f'current idle period: {current_idle_period}')
                    if current_idle_period > 5:
                        # scrn.blur_text(current_idle_period-5)
                        blur_text(current_idle_period-4)
                else:
                    # scrn.blur_text(0)
                    blur_text(0)
                    current_idle_period = 0
                    scrn.ids["circular_bar"].value = 1
                    current_text = scrn.text_i.text

            if timer_force_stop:
                # scrn.blur_text(0)
                blur_text(0)
                print("TIMER WAS STOPPED MANUALLY")
            else:
                if switch_screens == True:
                    blur_text(0)
                    # print("TIMER WAS STOPPED DUE TO SWITCHING SCREENS")
                else:
                    blur_text(10)
                    # print("YOU PAUSED WRITING FOR TOO LONG")
                    if full_screen == True:
                        scrn.ids.exit_full_screen_hidden.trigger_action(0.1)
                    else:
                        scrn.ids.save_button.trigger_action(0.1)
                        scrn.ids.restart_button.pos_hint = {"top": 0.995, "right": 0.86}

                   

        input_wait_thread = threading.Thread(target=run_timer)
        input_wait_thread.start()

    

Factory.register('WritingScreen', cls=root)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == '__main__':
    TypeOrDie().run()
    


