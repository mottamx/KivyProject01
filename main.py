# main.py
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout

from zeroconf import Zeroconf, ServiceBrowser
import ipaddress

class MainApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.menu_items = []
        self.enabledVar = False  # Initialize as False
    
        return Builder.load_file('main.kv')

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
    
MainApp().run()
