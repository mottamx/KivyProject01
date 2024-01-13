from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager

class Screen1(Screen):
    pass

class Screen2(Screen):
    pass

class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Screen1(name="screen1"))
        sm.add_widget(Screen2(name="screen2"))
        return sm

# class MainWidget(Widget):
#     def __init__(self, **kwargs):
#         super(MainWidget, self).__init__(**kwargs)

if __name__ == '__main__':
    app = MainApp()
    app.run()