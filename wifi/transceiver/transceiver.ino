#include <SPI.h>
#include <WiFiNINA.h>

///////please enter your sensitive data
char ssid[] = "M201";        // your network SSID (name)
char pass[] = "WacManIDP";    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                 // your network key index number (needed only for WEP)

int status = WL_IDLE_STATUS;
WiFiServer server(80);

void setup() {
  Serial.begin(9600);      // initialize serial communication

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to Network named: ");
    Serial.println(ssid);                   // print the network name (SSID);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);
    // wait 10 seconds for connection:
    delay(10000);
  }
  server.begin();                           // start the web server on port 80
  printWifiStatus();                        // you're connected now, so print out the status
}

String wifiWrapper(int d){
  WiFiClient client = server.available(); // listen for incoming clients

  if (client){                            // if you get a client 
    String currentLine = "";              // make a String to hold incoming data from the client
    while (client.connected()){           // loop while the client's connected
      if (client.available()){            // if there's bytes to read from the client,
        char c = client.read();           // read a byte, then
        Serial.write(c);                  // print it out the serial monitor
        if (c == '\n'){                   // if the byte is a newline character

          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the HTTP request, so check to see if the client request was "GET /S" or "GET /R"
          if (currentLine.length() == 0){
          }
        } else{             // if you get a newline, then clear currentLine:
          currentLine = "";
        }
      }
      else if (c != '\r'){                // if you got anything else but a carriage return character,
        currentLine += c;                 // add it to the end of the currentLine
      }
    }
  }  
}

void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
  // print where to go in a browser:
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
}
