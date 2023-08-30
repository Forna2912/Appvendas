from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from myfirebase import MyFireBase
from datetime import date

# Load the KV file
GUI = Builder.load_file('main.kv')

class LoadingScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class MyApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoadingScreen(name='loading'))
        self.sm.add_widget(MainScreen(name='main'))
        
        # Use Clock.schedule_once to switch to the main screen after a delay
        Clock.schedule_once(self.load_main_screen, 1)  # Change the delay time as needed
        
        Window.softinput_mode = 'below_target'
        return self.sm
    
    def load_main_screen(self, dt):
        self.firebase = MyFireBase()  # Initialize your Firebase module
        self.sm.current = 'main'

if __name__ == '__main__':
    MyApp().run()
