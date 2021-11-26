#include <SPI.h>
#include <WiFiNINA.h>

const char* ssid = "Walker";
const char* password =  "bruhbruhbruh";

const uint16_t port = 8090;
//const char * host = "192.168.137.1";
IPAddress gateway;

String msg = "";
void setup()
{

  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }

  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());

  // Cheeky tactic where I reckon the server IP is always the gateway IP
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
  
    client.print("Hello from Arduino!");

    while(true){
      //If new data from server
      if(client.available()){
        while(Serial.available()){
          client.print(Serial.read());
        }

        //Add to string and do checking stuff
        char c = client.read();
        Serial.print(c);
        msg += c;
        if(c == '\n'){

          //This don't work because it checks if it starts with o or n so it's always true :(
          if(msg.startsWith("on")){
            Serial.println("Got on");
          }else if(msg.startsWith("off")){
            Serial.println("Got off");
          }else{
            Serial.println("Don't recognise");
          }

          //Can send if you want but we've already sent c
//         client.print(msg);
        }
      }
    }

    //How you disconnect
//    Serial.println("Disconnecting...");
//    client.stop();

    delay(10000);
}
