#include <WiFi.h>
#include <EEPROM.h>
#include <ESPmDNS.h>

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SSD1306_I2C_ADDRESS 0x3C
#define OLED_RESET -1

#define EEPROM_ADDRESS 0
#define EEPROM_SIZE 1024
#define MAX_CONNECTION_ATTEMPTS 3
#define RETRY_DELAY 10000  // 5 seconds delay between connection attempts
#define CLEAR_EEPROM_BUTTON_PIN 4


const char *ssid = "TypeTurbo";
const char *password = NULL;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
WiFiServer server(80);
IPAddress ip;

void setup() {
  Serial.begin(115200);
  EEPROM.begin(EEPROM_SIZE);
  delay(10);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
    
  delay(2000);  // Pausa de 2 segundos
  // Borrar la pantalla
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.clearDisplay();

  String storedSSID, storedPass;
  restoreCredentials(storedSSID, storedPass);
  
  if (storedSSID.length() > 0 && storedPass.length() > 0) {
      // Stored credentials exist, try to connect to the WiFi network
      Serial.println("Stored credentials exist");
      display.clearDisplay();//***//
      title("::Wifi::");
      secondline("Linking...");
      int statusInt = connectToWiFi(storedSSID, storedPass);
      if (statusInt == 1) {
        if (!MDNS.begin("turbo")) {
            Serial.println("Error setting up MDNS responder!");
            while(1){delay(1000);}
        }
        Serial.println("mDNS responder started");
        MDNS.addService("http", "tcp", 80);
        Serial.println(ip);
        display.clearDisplay();//***//
        title("::Wifi::");
        secondline("C to: " +storedSSID);
        thirdline(ip.toString());
      }else{
        display.clearDisplay();//***//
        title("ERROR");
        secondline("No pude conectarme");
        thirdline("Reiniciame");
      }
  } else {
      // No stored credentials, create an AP to receive new credentials
      Serial.println("No credentials found");
      display.clearDisplay();//***//
      title("TypeTurbo");
      secondline("Own WiFi");
      createAP();
  }
    
    pinMode(CLEAR_EEPROM_BUTTON_PIN, INPUT_PULLUP);
}

int connectToWiFi(const String& ssid, const String& pass) {
  int attempts = 0;
  Serial.println("connectToWiFi");
  while (attempts < MAX_CONNECTION_ATTEMPTS) {
    display.clearDisplay();//***//
    title("Conectando:");
    String texto = (String) (attempts+1);
    secondline("Attempt:" + texto);
    int status = WiFi.begin(ssid.c_str(), pass.c_str());
    if (status == WL_CONNECTED) {
      Serial.println("Connected to WiFi");
      ip = WiFi.localIP();
      server.begin();
      Serial.println(ip);
      return 1;
    } else {
      Serial.print("Connection attempt ");
      Serial.print(attempts + 1);
      Serial.println(" failed");
      delay(RETRY_DELAY);
      attempts++;
    }
  }
  if(attempts>=MAX_CONNECTION_ATTEMPTS){
    Serial.print("Unable to connect with given credentials ");
    //Start own Wifi
    createAP();
    Serial.print("Own AP started");
    display.clearDisplay();//***//
    title("TypeTurbo");
    secondline("Own WiFi");
    return 0;
  }
  return 0;// Default return if the loop exits for some reason without hitting MAX_CONNECTION_ATTEMPTS
}

void createAP() {
  // Your code to create an AP and handle new credentials...
  WiFi.softAP(ssid, password);
  Serial.println("Selfserving in: ");
  Serial.println(WiFi.softAPIP());
  server.begin();
  Serial.println("Self AP is live.");
  display.clearDisplay();//***//
  title("TypeTurbo");
  secondline(".....Own WiFi.....");
}

void saveCredentials(const String& ssid, const String& pass) {
  for (int i = 0; i < ssid.length(); ++i) {
    EEPROM.write(EEPROM_ADDRESS + i, ssid[i]);
  }
  EEPROM.write(EEPROM_ADDRESS + ssid.length(), '\0');
  int passOffset = EEPROM_ADDRESS + ssid.length() + 1;
  for (int i = 0; i < pass.length(); ++i) {
    EEPROM.write(passOffset + i, pass[i]);
  }
  EEPROM.write(passOffset + pass.length(), '\0');
  EEPROM.commit();
  Serial.println("Credentials saved");
}

void restoreCredentials(String& ssid, String& pass) {
  //SSID
  int i = 0;
  char currentChar = EEPROM.read(EEPROM_ADDRESS + i);
  while (currentChar != '\0' && i < 32) {
    ssid += currentChar;
    currentChar = EEPROM.read(EEPROM_ADDRESS + (++i));
  }
  //Passwd
  int passOffset = EEPROM_ADDRESS + i + 1;
  i = 0;
  currentChar = EEPROM.read(passOffset + i);
  while (currentChar != '\0' && i < 64) {
    pass += currentChar;
    currentChar = EEPROM.read(passOffset + (++i));
  }
  Serial.println("Restored SSID: " + ssid);
  //Serial.println("Restored" + pass);
}

void errorCode(const String& error, WiFiClient& client) {
  Serial.println("Error: " + error);
  client.println("HTTP/1.1 404 Not Found");
  client.println("Content-Type: text/html");
  client.println("");
  client.println("Error: " + error);
  client.stop();
}

void handleLiveRequest(WiFiClient& client) {
  Serial.println("Just passing list...");
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println("");
  client.println("TypeTurboIsAlive");
  client.stop();
}

void retrieveSavedCredentials(WiFiClient& client) {
  Serial.println("Retrieving credentrials...");
  String storedSSID, storedPass;
  restoreCredentials(storedSSID, storedPass);
  Serial.println(storedSSID);
  // Check if storedSSID is empty
  if (storedSSID.isEmpty()) {
    // If empty, respond with an error status code
    errorCode("Stored SSID not found", client);
  } else {
    // If not empty, respond with the stored SSID
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/html");
    client.println("");
    client.println("Stored SSID: " + storedSSID);
  }
  client.stop();
}

void handleKeysRequest(String requestLine, WiFiClient& client) {
  //Serial.println("Received:");
  //Serial.println(requestLine);
  int start = requestLine.indexOf("?") + 1;  // Index "?"
  int end = requestLine.indexOf(" HTTP");    // Index "HTTP"

  if (start != -1 && end != -1) {
    //Useful substring
    String params = requestLine.substring(start, end);
    //Serial.println(params);
    //Index & used to split
    int separatorIndex = params.indexOf("&");
    if (separatorIndex != -1) {
      String ssidParam = params.substring(0, separatorIndex);
      String passParam = params.substring(separatorIndex + 1);
      //Validate again
      if (ssidParam.startsWith("ssid=") && passParam.startsWith("pass=")) {
        
        String ssid = urldecode(ssidParam.substring(5));// Removes "ssid="
        String pass = urldecode(passParam.substring(5));// Removes "pass=" 
        Serial.println("SSID: " + ssid);
        Serial.println("Password: " + pass);
        Serial.println("Saving...");
        display.clearDisplay(); //***//
        title("Saving");
        secondline(ssid);
        saveCredentials(ssid, pass);
        client.println("HTTP/1.1 200 OK");
        client.println("Content-Type: text/html");
        client.println("");
        client.println("Saved");
        client.stop();
        display.clearDisplay(); //***//
        title("TypeTurbo");
        secondline("Reboot");
        delay(10000);  /*ESP32 Reset after 10 sec*/
        ESP.restart();  /*ESP restart function*/
      } else {
        Serial.println("Error: Missing (ssid/pass)");
        errorCode("Missing (ssid/pass)", client);
      }
    } else {
        errorCode("Missing '&'", client);
        Serial.println("Error: Missing '&'");
    }
  } else {
    errorCode("Bad URL", client);
    Serial.println("Error: Bad URL");
  }
  client.stop();
}

void clearEEPROM() {
  display.clearDisplay(); //***//
  title("BORRANDO");
  secondline("Red anterior");
  for (int i = 0; i < 512; i++) {
   EEPROM.write(i, 0);
   }
  EEPROM.commit();
  delay(500);
  Serial.println("EEPROM cleared");
}

String urldecode(const String &input) {
  String decoded = "";
  char a, b;
  for (size_t i = 0; i < input.length(); i++) {
    if (input[i] == '%') {
      a = input[i + 1];
      b = input[i + 2];
      i += 2;
      decoded += char((hexCharToInt(a) << 4) | hexCharToInt(b));
    } else {
      decoded += input[i];
    }
  }
  return decoded;
}

int hexCharToInt(char c) {
  if ('0' <= c && c <= '9') {
    return c - '0';
  } else if ('a' <= c && c <= 'f') {
    return c - 'a' + 10;
  } else if ('A' <= c && c <= 'F') {
    return c - 'A' + 10;
  }
  return 0;
}

void title(String text) {
  //Serial.print("title");
  display.setTextSize(2);
  display.setCursor(0,0);
  display.println(text);
  display.display();
}
void secondline(String text2) {
  //Serial.print("secondline");
  display.setTextSize(1);
  display.setCursor(0,17);
  display.println(text2);
  display.display();
}
void thirdline(String text3) {
  //Serial.print("secondline");
  display.setTextSize(1);
  display.setCursor(0,30);
  display.println(text3);
  display.display();
}
void loop() {
  if (digitalRead(CLEAR_EEPROM_BUTTON_PIN) == LOW) {
    // Button is pressed, clear EEPROM
    clearEEPROM();
    delay(1000);  // Debounce delay
  }
  
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  // Wait for the client to send a request
  while (!client.available()) {
    delay(1);
  }

  String requestLine = client.readStringUntil('\r');
  //Serial.println("Received:");
  Serial.println(requestLine);
  if (requestLine.indexOf("/keys") != -1) {
    handleKeysRequest(requestLine,client);
  } else if (requestLine.indexOf("/live") != -1) {
    handleLiveRequest(client);
  } else if (requestLine.indexOf("/nets") != -1){
    retrieveSavedCredentials(client);
  } else if (requestLine.indexOf("/clear") != -1){
    clearEEPROM();
    delay(2000);  /*ESP32 Reset after 2 sec*/
    Serial.println("Restart");
    ESP.restart();  /*ESP restart function*/
  }
}

//keys; live; nets; clear;