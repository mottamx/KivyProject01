# main.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout

class MenuWidget(BoxLayout):
    pass

class MainScreen(Screen):
    pass

class ConfigScreen(Screen):
    pass

class MainApp(App):
    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ConfigScreen(name='config'))
        return sm

if __name__ == '__main__':
    MainApp().run()
