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
from kivymd.uix.snackbar import Snackbar
from zeroconf import Zeroconf, ServiceBrowser


import ipaddress


class InitialScreen(Screen):
    pass

class IoTScreen(Screen):

    def on_submit_button_press(self):
        # Receive the Wifi config
        app = MDApp.get_running_app()
        app.ssid_text = self.ids.ssid.text
        app.pass_text = self.ids.passw.text
        if not app.ssid_text or not app.pass_text:
            # Show a Snackbar warning if either field is empty
            Snackbar(
                text="No pueden estar vacios SSID o password",
                duration=2,
                bg_color=(1, 0, 0, 1),
            ).open()
        else:
            #print(app.ssid_text + " " + app.pass_text)
            # Clear the MDTextField widgets
            self.ids.ssid.text = ""
            self.ids.passw.text = ""
            app.screen_manager.current = "iotinfo_screen"

    def toggle_password_visibility(self):
        # print("Visibility")
        pass_field = self.ids.passw
        pass_field.password = not pass_field.password
        pass_field.password_mask = '*' if pass_field.password else ''
        self.ids.passw_eye.icon = 'eye' if pass_field.password else 'eye-off'

class IoTInfoScreen(Screen):
    
    def on_tolink_btn_press(self):
        app = MDApp.get_running_app()
        print(f"Second hop: {app.ssid_text} {app.pass_text}")
        app.screen_manager.current = "linking_screen"

class LinkingScreen(Screen):
    def __init__(self, **kwargs):
        super(LinkingScreen, self).__init__(**kwargs)
        # Reference the Carousel declared in kv
        self.link_car = self.ids.link_car
        self.current_slide_index = 0  # Variable to store the current slide 
        # Bind the function to the on_touch_move event
        self.link_car.bind(on_touch_move=self.carousel_on_touch_move)
        # Start the first step
        self.check_esp_availability()
        
    def carousel_on_touch_move(self, instance, touch):
        if self.link_car.current_slide != self.current_slide_index:
            # If the current slide doesn't match the stored index, move back
            self.link_car.load_slide(self.link_car.slides[self.current_slide_index])
              
    def check_esp_availability(self):
        # Check if ESP is available
        
        # Move to the next slide if successful, else go back to the previous slide
        #self.link_car.load_slide(self.link_car.slides[1])
        pass

    def exchange_credentials(self):
        # Encrypt and exchange credentials with ESP
        # Move to the next slide if successful, else go back to the previous slide
        pass

    def wait_for_connection(self):
        # Wait for ESP to connect to the network
        # Move to the next slide if successful, else go back to the previous slide
        pass

    def on_pre_enter(self):
        # This method will be called before the screen is shown
        pass

class MainApp(MDApp):
    def build(self):
        self.ssid_text = ""
        self.pass_text = ""
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        # Builder.load_file('main.kv')
        self.enabledVar = False  # Initialize as False
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(InitialScreen(name="initial_screen"))
        self.screen_manager.add_widget(IoTScreen(name="iot_screen"))
        self.screen_manager.add_widget(IoTInfoScreen(name="iotinfo_screen"))
        self.screen_manager.add_widget(LinkingScreen(name="linking_screen"))
        Builder.load_file('main.kv')
        return self.screen_manager

    def connect_button_pressed(self):
        # Implement the action for the Update button press here
        #print("Connect button pressed")
        pass

    def update_button_pressed(self):
        # Implement the action for the Update button press here
        # print("Update button pressed")
        self.root.ids.button.md_bg_color = self.theme_cls.primary_color
        zeroconf = Zeroconf()
        listener = MyListener(self)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        self.enabledVar = True

    def on_icon_button_press(self):
        # Switch to the configuration screen
        #print("Connect on_icon_button_press pressed")
        self.screen_manager.current = "iot_screen"

    def on_goback_button_press(self):
        self.screen_manager.current = "initial_screen"


class MyListener:
    def __init__(self, app):
        self.app = app  # Store a reference to the app
        self.scanning = True

    def remove_service(self, zeroconf, type, name):
        # print("Service removed", name)
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        # print("Service added", name)
        byte_sequence = info.addresses[0]
        ip_address = ipaddress.IPv4Address(byte_sequence).exploded
        print("  Address:", ip_address)
        # print("  Port:", info.port)
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
