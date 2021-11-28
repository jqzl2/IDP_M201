// References: https://realpython.com/python-sockets/#background; https://techtutorialsx.com/2018/05/17/esp32-arduino-sending-data-with-socket-client/

#include <SPI.h>
#include <WiFiNINA.h>
 
const char* ssid = "M201";
const char* password =  "WacManIDP";
 
const uint16_t port = 8090;
//const char * host = "0.0.0.0";
IPAddress gateway;
 
void setup()
{
 
  Serial.begin(9600);
 
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
 
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());

  gateway = WiFi.gatewayIP();
}
 
void loop()
{
    WiFiClient client;
 
    if (!client.connect(gateway, port)) {
 
        Serial.println("Connection to host failed");
 
        delay(1000);
        return;
    }
 
    Serial.println("Connected to server successful!");
    int mode = 3;
    client.print(mode);
    
    while (true){
      if (client.available()){   // if there are bytes to read from the client
      while(Serial.available()){
        client.print(Serial.read());
      }
      char c = client.read();   // read a byte
      Serial.print(c);          // then print it out the serial monitor
      if (c == "$"){
        break;}
      }
    }
    client.stop();
    Serial.println("Client disconnected");
 
    delay(10000);
    }
