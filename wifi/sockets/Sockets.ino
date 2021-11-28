// References: https://realpython.com/python-sockets/#background; https://techtutorialsx.com/2018/05/17/esp32-arduino-sending-data-with-socket-client/

#include <SPI.h>
#include <WiFiNINA.h>
 
const char* ssid = "M201";
const char* password =  "WacManIDP";
 
const uint16_t port = 8090;
//const char * host = "0.0.0.0";
IPAddress gateway;
 
void setup(){                  // connected Arduino to PC mobile hotspot over WiFi
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
 
WiFiClient set_up_server(){     // connect Arduino to Sockets server created on the PC (improvement: make client a global variable by declaring before void setup() i.e. outside of any function)
    WiFiClient client;
    while(true){ 
      if (!client.connect(gateway, port)) {
          Serial.println("Connection to host failed");
      }
      
      else{
      Serial.println("Connected to server successful!");
      return client;
      }
  }
}

String send_mode_receive_path(WiFiClient client, int mode){      // send dummy mode to server, and then receive the PC's next commands
      String commands = "";
      client.print(mode);
      while(true){   // if there are bytes to read from the client
      if(client.available()){
      
      char c = client.read();   // read a byte
      Serial.print(c);          // then print it out the serial monitor
      commands += c;
      if (c == '$'){
        return commands;                  // end of command signposted by '$', so stop trying to read incoming data from PC
        }         
    }

    //command = "";    // clear command line
    //client.stop(); 
    //delay(10000);
  }
  return commands;
}

/*int main(){
  WiFiClient client = set_up_server();
  int mode = 3;
  String command = send_mode_receive_path(client, mode);
  Serial.println(command);
  return 0;
}*/

void loop(){
  WiFiClient client = set_up_server();
  while(true){
    int mode = 3;
    //String command = send_mode_receive_path(client, mode);
    Serial.println(send_mode_receive_path(client,mode));
  }
}
