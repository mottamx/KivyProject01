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
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import ipaddress
from ping3 import ping, verbose_ping


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
            # print(app.ssid_text + " " + app.pass_text)
            # Clear the MDTextField widgets
            #self.ids.ssid.text = ""
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
        # print(f"Second hop: {app.ssid_text} {app.pass_text}")
        app.screen_manager.current = "linking_screen"
        # print(f"Gone from here")


class LinkingScreen(Screen):
    def __init__(self, **kwargs):
        super(LinkingScreen, self).__init__(**kwargs)
        # Reference the Carousel declared in kv
        self.link_car = self.ids.link_car
        self.current_slide_index = 0  # Current slide
        # Bind the function to the on_touch_move event
        self.link_car.bind(on_touch_move=self.carousel_on_touch_move)

    def on_enter(self, *args):
        # print("Starting linking")
        self.update_progress(10)
        self.check_esp_availability()

    def update_progress(self, value):
        self.ids.progress_bar.value = value

    def carousel_on_touch_move(self, instance, touch):
        if self.link_car.current_slide != self.current_slide_index:
            # If the current slide doesn't match the stored index, move back
            self.link_car.load_slide(
                self.link_car.slides[self.current_slide_index])

    def check_esp_availability(self):
        app = MDApp.get_running_app()
        print("check_esp_availability")
        url = "http://192.168.4.1/live"
        req = UrlRequest(url, on_success=self.on_request_success, on_failure=lambda req,
                         result, app=app: self.on_request_failure(req, result, app), timeout=2)


    def on_request_success(self, req, result):
        #headers = req.resp_headers
        #print(f"on_request_success")
        self.update_progress(40)
        receivedStr = req.result.strip()
        #print(f"Received : {receivedStr}") #Comparemos esta
        if receivedStr == "TypeTurboIsAlive":
            print(f"Success, next step...")
            self.current_slide_index = 1
            self.link_car.load_next()
            self.exchange_credentials()

    def on_request_failure(self, req, result, app):
        print(f"Failed to receive data: {result}")
        app.screen_manager.current = "iotinfo_screen"
        Snackbar(
            text="Asegurate de estar conectado a TypeTurbo",
            duration=2,
            bg_color=(1, 0, 0, 1),
        ).open()

    def exchange_credentials(self):
        app = MDApp.get_running_app()
        # Encrypt and exchange credentials with ESP
        print("exchange_credentials")
        self.update_progress(50)
        #print(f"Third hop: {app.ssid_text} {app.pass_text}")
        urlRawCred = f"http://192.168.4.1/keys?ssid={
            app.ssid_text}&pass={app.pass_text}"
        print(urlRawCred)
        req = UrlRequest(urlRawCred, on_success=self.on_request_second, on_failure=lambda req,
                         result, app=app: self.on_request_failure(req, result, app), timeout=2)
        
    def on_request_second(self, req, result):
        # Called on successful UrlRequest
        print(f"Received: {result}")
        if result.strip() == "Saved":
            print(f"Success, next step...")
            self.current_slide_index = 2
            self.link_car.load_next()
            self.wait_for_connection()
        
    def wait_for_connection(self):
        # Wait for ESP to connect to the network
        print("wait_for_connection")
        self.update_progress(70)
        zeroconf = Zeroconf()
        listener = MyListener(self)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        # Schedule the check_ip_address method to be called every 1 seconds
        print(f"Got {self.ip_address}")
        Clock.schedule_interval(self.check_ip_address, 1)

    def check_ip_address(self, dt):
        # Check if the IP address is available
        if self.ip_address != "":
            print(f"Got {self.ip_address}, success")
            # Stop the Clock schedule when the IP address is found
            Clock.unschedule(self.check_ip_address)
            self.current_slide_index = 3
            self.link_car.load_next()
            print(f"Got {self.ip_address}, success")
        else:
            self.timeout_iterations -= 1
            if self.timeout_iterations <= 0:
                print("Timeout reached. IP address not found.")
                # Stop the Clock schedule when the timeout is reached
                Clock.unschedule(self.check_ip_address)


class MainApp(MDApp):
    def build(self):
        self.ssid_text = ""
        self.pass_text = ""
        self.ip_address = ""
        self.timeout_iterations = 3  # Adjust as needed
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
        # print("Connect button pressed")
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
        # print("Connect on_icon_button_press pressed")
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
        self.ip_address = ipaddress.IPv4Address(byte_sequence).exploded
        print("  Address:", self.ip_address)
        # print("  Port:", info.port)
        if info.addresses:
            self.app.root.ids.button.text = f"{self.ip_address}"
            self.app.root.ids.button.md_bg_color = self.app.theme_cls.accent_color
            self.scanning = False
            zeroconf.close()
            print("Zero closed")

    def update_service(self, zeroconf, service_type, service_name):
        # Placeholder for the update_service method
        pass


if __name__ == "__main__":
    MainApp().run()
