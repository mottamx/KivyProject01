# main.py
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from kivy.uix.screenmanager import ScreenManager, Screen
from zeroconf import Zeroconf, ServiceBrowser
import ipaddress

class InitialScreen(Screen):
    pass

class IoTScreen(Screen):
    def on_submit_button_press(self):
        # Receive the Wifi config
        ssid_text = self.ids.ssid.text
        pass_text = self.ids.passw.text
        print(ssid_text + " " + pass_text)
        self.manager.current = "initial_screen"

    def toggle_password_visibility(self):
        print("Visibility")
        pass_field = self.ids.passw
        pass_field.password = not pass_field.password
        pass_field.password_mask = '*' if pass_field.password else ''
        self.ids.passw_eye.icon = 'eye' if pass_field.password else 'eye-off'


class MainApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        # Builder.load_file('main.kv')
        self.enabledVar = False  # Initialize as False
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(InitialScreen(name="initial_screen"))
        self.screen_manager.add_widget(IoTScreen(name="iot_screen"))
        Builder.load_file('main.kv')
        return self.screen_manager


    def connect_button_pressed(self):
        # Implement the action for the Update button press here
        print("Connect button pressed")
        
    def update_button_pressed(self):
        # Implement the action for the Update button press here
        #print("Update button pressed")
        self.root.ids.button.md_bg_color = self.theme_cls.primary_color
        zeroconf = Zeroconf()
        listener = MyListener(self)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        self.enabledVar = True
    
    def on_icon_button_press(self):
        # Switch to the configuration screen
        print("Connect on_icon_button_press pressed")
        self.screen_manager.current = "iot_screen"




class MyListener:
    def __init__(self, app):
        self.app = app  # Store a reference to the app
        self.scanning = True 
        
    def remove_service(self, zeroconf, type, name):
        #print("Service removed", name)
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        #print("Service added", name)
        byte_sequence = info.addresses[0]
        ip_address = ipaddress.IPv4Address(byte_sequence).exploded
        print("  Address:", ip_address)
        #print("  Port:", info.port)
        if info.addresses:
            self.app.root.ids.button.text = f"{ip_address}"
            self.app.root.ids.button.md_bg_color = self.app.theme_cls.accent_color
            self.scanning = False
            zeroconf.close()
            print("Zero closed")

    def update_service(self, zeroconf, service_type, service_name):
        # Placeholder for the update_service method
        pass
 
if __name__ == "__main__":
    MainApp().run()
