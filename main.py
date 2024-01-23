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
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from kivy.network.urlrequest import UrlRequest
import requests
from kivy.clock import Clock
import ipaddress
from functools import partial


class InitialScreen(Screen):
    pass
    # def connect_device(self):
    #     print(f"connect_device IS")
        

class IoTScreen(Screen):

    def on_submit_button_press(self):
        # Receive the Wifi config
        app = MDApp.get_running_app()
        # app.ssid_text = self.ids.ssid.text
        app.pass_text = self.ids.passw.text
        app.ssid_text = self.ids.ssid.text.replace(" ", "%20")

        if not app.ssid_text or not app.pass_text:
            # Show a Snackbar warning if either field is empty
            Snackbar(
                text="No pueden estar vacios SSID o password",
                duration=2,
                bg_color=(1, 0, 0, 1)
            ).open()
        else:
            # print(app.ssid_text + " " + app.pass_text)
            # Clear the MDTextField widgets
            # self.ids.ssid.text = ""
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
        self.update_progress(5)
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
        #print("check_esp_availability")
        url = "http://192.168.4.1/live"
        req = UrlRequest(url, on_success=self.on_request_success, 
                         on_error=lambda req,result, app=app: self.on_request_failure(req, result, app), timeout=3)
   
    def on_request_success(self, req, result):
        # headers = req.resp_headers
        #print(f"on_request_success")
        receivedStr = req.result.strip()
        # print(f"Received : {receivedStr}") #Comparemos esta
        if receivedStr == "TypeTurboIsAlive":
            #print(f"Success, next step...")
            self.current_slide_index = 1
            self.link_car.load_next()
            self.update_progress(30)
            self.exchange_credentials()

    def on_request_failure(self, req, result, app):
        #print(f"Failed to receive data: {result}")
        self.update_progress(0)
        self.current_slide_index = 0
        app.screen_manager.current = "iotinfo_screen"
        Snackbar(
            text="Asegurate de estar conectado a TypeTurbo",
            duration=2,
            bg_color=(1, 0, 0, 1),
        ).open()

    def exchange_credentials(self):
        #print("exchange_credentials")
        app = MDApp.get_running_app()
        # Encrypt and exchange credentials with ESP
        # print(f"Third hop: {app.ssid_text} {app.pass_text}")
        urlRawCred = f"http://192.168.4.1/keys?ssid={
            app.ssid_text}&pass={app.pass_text}"
        self.current_slide_index = 2
        self.link_car.load_next()
        self.update_progress(50)
        req = UrlRequest(urlRawCred, on_success=self.on_request_second, 
                         on_error=lambda req,result, app=app: self.on_request_failure(req, result, app), timeout=3)

    def on_request_second(self, req, result):
        # Called on successful UrlRequest
        #print(f"Received: {result}")
        if result.strip() == "Saved":
            #print(f"Success on_request_second")
            Snackbar(
                text="Cambia a la red WiFi del formulario",
                duration=5,
                bg_color=(0.176, 0.184, 0.243, 1)
            ).open()
            self.current_slide_index = 3
            self.link_car.load_next()
            # Wait 15 secs to have time to change network
            Clock.schedule_once(self.wait_for_connection, 20)  

    def wait_for_connection(self, dt):
        app = MDApp.get_running_app()
        self.current_slide_index = 4
        self.link_car.load_next()
        self.update_progress(70)
        #print("wait_for_connection")
        zeroconf = Zeroconf()
        listener = MyListener(self)
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        # Schedule the wait_for_ip, check every 5 seconds
        app.event = Clock.schedule_interval(partial(self.wait_for_ip_initial, listener=listener, zeroconf=zeroconf), 2)
        print(f"Waiting for {app.ip_address}...")

    def wait_for_ip_initial(self, dt, listener, zeroconf):
        print("Checking for IP")
        app = MDApp.get_running_app()
        if app.ip_address:
            #print(f"Found : {app.ip_address}")
            zeroconf.close()
            app.screen_manager.current = "initial_screen"
            app.event.cancel()
            Snackbar(
                text="Exito, dispositivo configurado",
                duration=2,
                bg_color=(0.176, 0.184, 0.243, 1)
            ).open()
        # *******UPDATE THE BUTTON THAT CONNECTS ON INITIAL SCREEN
        screen_manager = self.root
        initial_screen = screen_manager.get_screen('initial_screen')
        s1_connect_button = initial_screen.ids.s1_connect
        s1_connect_button.text =  f"CONECTAR A TURBOTYPE \n {app.ip_address}"
        s1_connect_button.disabled = False
        s1_connect_button.md_bg_color = app.theme_cls.accent_color

class MainApp(MDApp):
    def build(self):
        app = MDApp.get_running_app()
        self.ssid_text = ""
        self.pass_text = ""
        app.ip_address = ""
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(InitialScreen(name="initial_screen"))
        self.screen_manager.add_widget(IoTScreen(name="iot_screen"))
        self.screen_manager.add_widget(IoTInfoScreen(name="iotinfo_screen"))
        self.screen_manager.add_widget(LinkingScreen(name="linking_screen"))
        Builder.load_file('main.kv')
        return self.screen_manager

    def update_ip_device(self):
        app = MDApp.get_running_app()
        print(f"update_ip_device")
        if (not app.ip_address):
            print(f"Missing IP {app.ip_address}")
            zeroconf = Zeroconf()
            listener = MyListener(self)
            browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
            # Schedule the wait_for_ip, check every 5 seconds
            app.event = Clock.schedule_interval(partial(self.wait_for_ip, listener=listener, zeroconf=zeroconf), 2)
            print(f"Waiting for {app.ip_address}...")
    
    def connect_device(self):
        print(f"connect_device MainApp")
        screen_manager = self.root
        initial_screen = screen_manager.get_screen('initial_screen')
        s1_update_button = initial_screen.ids.s1_update
        s1_update_button.disabled = False        

        
    def connect_button_pressed(self):
        # Implement the action for the Update button press here
        print("Connect button pressed")

    def update_button_pressed(self): ##REMOVE 
        print("update_button_pressed")

    def wait_for_ip(self, dt, listener, zeroconf):
        screen_manager = self.root
        initial_screen = screen_manager.get_screen('initial_screen')
        s1_connect_button = initial_screen.ids.s1_connect
        s1_update_button = initial_screen.ids.s1_update
        print("wait_for_ip")
        app = MDApp.get_running_app()
        if (app.ip_address):
            print(f"Found : {app.ip_address}")
            zeroconf.close()
            app.event.cancel()
            s1_connect_button.text = f"CONECTAR A TURBOTYPE \n {app.ip_address}"
            s1_connect_button.disabled = False
            s1_connect_button.md_bg_color = app.theme_cls.accent_color
            s1_update_button.disabled = True
            Snackbar(
                text="Exito, dispositivo encontrado",
                duration=2,
                bg_color=(0.176, 0.184, 0.243, 1)
            ).open()


    def on_icon_button_press(self):
        # Switch to the configuration screen
        # print("Connect on_icon_button_press pressed")
        self.screen_manager.current = "iot_screen"

    def on_goback_button_press(self):
        self.screen_manager.current = "initial_screen"


class MyListener:
    def __init__(self, app):
        app = MDApp.get_running_app()

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        app = MDApp.get_running_app()
        info = zc.get_service_info(type_, name)
        print(f"Service {name} found")
        if (name == 'turbo._http._tcp.local.'):
            # print(f"EUREKA")
            byte_sequence = info.addresses[0]
            app.ip_address = ipaddress.IPv4Address(byte_sequence).exploded
            print(f"Service {name} added, service addresses=: {app.ip_address}")


if __name__ == "__main__":
    MainApp().run()
