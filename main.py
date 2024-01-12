from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget

class MainApp(App):
    def build(self):
        pass

class MainWidget(Widget):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)

if __name__ == '__main__':
    app = MainApp()
    app.run()