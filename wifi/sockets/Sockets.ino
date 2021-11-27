// References: https://realpython.com/python-sockets/#background; https://techtutorialsx.com/2018/05/17/esp32-arduino-sending-data-with-socket-client/

#include <SPI.h>
#include <WiFiNINA.h>

/*char ssid[] = "M201";
char pass[] =  "WacManIDP";

int status = WL_IDLE_STATUS;
const uint16_t port = 8090;
//const char * host = "192.168.137.1";
IPAddress gateway;

String msg = ""; // String to hold data received from Python sockets server

void setup()
{
 
  Serial.begin(115200);
 
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
 
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
 
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
  
    client.print(2);

    while(true){
      //If new data from server
      if(client.available()){
        while(Serial.available()){
          client.print(Serial.read());
        }

        // Add to string and do checking stuff
        char c = client.read();
        Serial.print(c);
        msg += c;
        if(c == '\n'){

          //Can send if you want but we've already sent c
//         client.print(msg);
        }
      }
    }

    //How you disconnect
    Serial.println("Disconnecting...");
    client.stop();

    delay(10000);
}*/
 
const char* ssid = "M201";
const char* password =  "WacManIDP";
 
const uint16_t port = 8090;
const char * host = "0.0.0.0";
 
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
 
}
 
void loop()
{
    WiFiClient client;
 
    if (!client.connect(host, port)) {
 
        Serial.println("Connection to host failed");
 
        delay(1000);
        return;
    }
 
    Serial.println("Connected to server successful!");
 
    client.print(3);

    while (client.connected()){   // loop while the client is connected
      if (client.available()){    // if there are bytes to read from the client
        char c = client.read();   // read a byte
        Serial.write(c);          // then print it out the serial monitor
      }

      else{
        break;
      }
    }
    
    client.stop();
    Serial.println("Client disconnected");
 
    delay(10000);
}
