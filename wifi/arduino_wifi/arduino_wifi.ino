#include <Adafruit_MotorShield.h>
#include "SharpIR.h"
#include <Servo.h>
#include <math.h>
#include <SPI.h>
#include <WiFiNINA.h>
#include <string.h>

#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                 // your network key index number (needed only for WEP)

int status = WL_IDLE_STATUS;
WiFiServer server(80);
String readString;

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


String wifiWrapper(int d) {
    WiFiClient client = server.available(); // listen for incoming clients

    while (!client) {
        client = server.available();
    }
    
    if (client) { // if you get a client,
        String currentLine = ""; // make a String to hold incoming data from the client
        String request;
        while (client.connected()) { // loop while the client's connected
            if (client.available()) { // if there's bytes to read from the client,
                char c = client.read(); // read a byte, then
                Serial.write(c); // print it out the serial monitor
                if (c == '\n') { // if the byte is a newline character

                    // if the current line is blank, you got two newline characters in a row.
                    // that's the end of the client HTTP request, so send a response:
                    if (currentLine.length() == 0) {
                        // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
                        // and a content-type so the client knows what's coming, then a blank line:
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:text/plain");
                        client.println();

                        // the content of the HTTP response follows the header:
                        client.print("Arduino has received PC commands");

            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            break;
          } else {    // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } 
        else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
          request += c;
        }
      }
    }
 }

void loop(){
  String commands;
  String request = wifiWrapper();
  char * crequest = new char [request.length() + 1];
  strcpy(crequest, request.c_str());
  char * data = strtok(crequest, "!");
  
  int i = 0;
  while (data != 0 && i < 4){
    i += 1;
    //Serial.println(data);
    data = strtok(NULL, "!");
    if (i == 1){
      commands = data;
      break;
    }
  }
  delete[] crequest;
  Serial.println(commands);

  int count = 0;
  char * ccommands = new char [commands.length() + 1];
  strcpy(ccommands, commands.c_str());
  char * command = strtok(ccommands, ".");
  while (command != 0){    
    Serial.println(command);

    //String parsingArray = strtok(command , ",");

    int operation = strtok(command , ",").toInt(); // turn/goto/dummymode
    int input1 = strtok(NULL , ",").toInt(); //
    int input2 = strtok(NULL , ",").toInt(); // 
    

    switch(operation){
      case 0:
      //goTo
        break;
    }

    dt *= 1000;
    int start = millis();

    while (millis() - start < dt and digitalRead(lineSensorPin) == 0) {

        adjustDrive(sideGoal, 1);
    }

    drive(255, 255);
    delay(500);
    openDoor();
    drive(-255, -255);
    delay(500);

    //make sure wheels always end neutral
    drive(0, 0);
}

// this is a wrapper to deal with the carrying logic
// the robot does each goTo multiple times to account for bad sensor reads
void goToDistanceWrapper(int goal, int sideGoal) {
    if (carrying) {
        goToDistance(goal + 30, sideGoal);
        goToDistance(goal + 30, sideGoal);
        goToDistance(goal + 30, sideGoal);
        goToDistance(goal + 30, sideGoal);
        goToDistance(goal + 30, sideGoal);
        goToDistance(goal + 30, sideGoal);
        maintainDistance(2000, sideGoal);
        drive(0, 0);

    } else {
        goToDistance(goal, sideGoal);
        goToDistance(goal, sideGoal);
        goToDistance(goal, sideGoal);
    }

    delay(100);

    if (abs(distanceFront() - goal) / goal > 0.05 and carrying == false) {
        goToDistanceWrapper(goal, sideGoal);
    }
}
//general movement code
void goToDistance(int goal, int sideGoal) {

    //setting up local variables
    int rightSpeed = MaxPower;
    int leftSpeed = MaxPower;
    int sign = 1;
    float mult;

    //setting up forwards vs backwards movement
    if (goal > distanceFront()) {
        sign = -1;
    }
    rightSpeed *= sign;
    leftSpeed *= sign;

    //starting the robot off
    drive(rightSpeed, leftSpeed);

    //if the goal distance is not yet reached
    while (sign * distanceFront() > sign * goal) {
        if (sideGoal) {
            adjustDrive(sideGoal, sign);
        }
    }

    //make sure wheels always end neutral
    drive(0, 0);
}

//this is the same as goTo but instead it aims to drive straight (near a wall) for a time
void maintainDistance(int deltaTime, int sideGoal) {
    //setting up local variables
    int rightSpeed = MaxPower;
    int leftSpeed = MaxPower;
    float mult;
    float dt;
    dt = deltaTime;
    int start = millis();

    while (millis() - start < dt) {
        adjustDrive(sideGoal, 1);
    }

    //make sure wheels always end neutral
    drive(0, 0);
}

//this is the code that adjusts the robot speeds to follow walls
void adjustDrive(int sideGoal, int sign) {
    float mult;
    int rightSpeed, leftSpeed;

    //mult is the difference between the side goal and value
    mult = (float) distanceSide() / (float) sideGoal;
    mult = 1 - mult;

    //feedback factors for fine tuning if required
    mult *= feedBackFactor;

    //if its too far out or too close
    if (mult < 0) {
        rightSpeed = MaxPower * (1 + mult);
        leftSpeed = MaxPower;
    } else {
        leftSpeed = (1 - mult) * MaxPower;
        rightSpeed = MaxPower;
    }

    //correction for forwards backwards
    leftSpeed *= sign;
    rightSpeed *= sign;

    //drive with corrected speed
    drive(rightSpeed, leftSpeed);

    //debugging prints
    Serial.println(distanceFront());
    Serial.println(distanceSide());
    Serial.println(rightSpeed);
    Serial.println(leftSpeed);
    Serial.println(mult);
    Serial.println("");

}

//this turns corners in a fixed radius, used for going around the obsticals
void turnCorner(int sign) {
    if (sign > 0) {
        drive(255, 75);
    } else {
        drive(75, 255);
    }

    delay(2000);

    //make sure wheels always end neutral
    drive(0, 0);
}

//this turns on the spot
void turnOnSpot(int n) {
    //n is the number of 90 degree turns
    if (n > 0) {
        drive(255, -255);
    } else {
        drive(-255, 255);
    }

    //rturn is calcualted assuming max speed at all times
    delay((int)(abs(n) * RTurn));

    //this is used to ensure that the robot is close to straight
    //not neccessary but makes robot run faster in the end
    while (angleSide() < 0) {
        delay(1);
    }

    //make sure wheels always end neutral
    drive(0, 0);
}

void openDoor() {
    leftServo.write(30);
    rightServo.write(120);
    carrying = false;
}

void closeDoor() {
    leftServo.write(90);
    rightServo.write(60);
    carrying = true;
}

//dummy collection logic
int collectDummy(int dummySide) {
    //special mode used to force the robot to use the US sensor
    collecting = true;

    //ensures that the doors are open
    openDoor();

    //get close to dummy
    goToDistance(0, dummySide);

    //detect mode
    int dummyMode = DiffDummy();

    //light up correct LED's
    if (dummyMode != 3) {
        digitalWrite(redPin, HIGH);
    } else {
        digitalWrite(redPin, LOW);
    }
    if (dummyMode != 2) {
        digitalWrite(greenPin, HIGH);
    } else {
        digitalWrite(greenPin, LOW);
    }

    //wait for at least 5 seconds
    delay(5555);

    //get closer to the dummy
    drive(255, 255);
    delay(238);
    drive(0, 0);

    //close doors

    closeDoor();

    //back to default mode handling
    collecting = false;

    //return mode
    return dummyMode;
}

void loop() {
    String commands;
    String request = wifiWrapper(3);
    char * crequest = new char[request.length() + 1];
    strcpy(crequest, request.c_str());
    char * data = strtok(crequest, "!");

    int i = 0;
    while (data != 0 && i < 4) {
        i += 1;
        //Serial.println(data);
        data = strtok(NULL, "!");
        if (i == 1) {
            commands = data;
            break;
        }
    }
    delete[] crequest;
    Serial.println(commands);

    int count = 0;
    char * ccommands = new char[commands.length() + 1];
    //strcpy(ccommands, commands.c_str());

    commands.toCharArray(ccommands, commands.length());

    char * command = strtok(ccommands, ".");

    count = 0;

    while (command != 0) {
        count += 1;

        String parsingArray = strtok(command, ",");

        int operation = parsingArray.toInt(); // turn/goto/dummymode
        parsingArray = strtok(0, ",");

        int input1 = parsingArray.toInt(); //

        parsingArray = strtok(0, ",");
        int input2 = parsingArray.toInt(); // 

        switch (operation) {
        case 0:
            goToDistanceWrapper(input1, input2);
            //go to
            break;

        case 1:
            turnOnSpot(input1);
            //turn on spot
            break;

        case 2:

            collectDummy(input1);

            //collect dummy
            break;

        case 3:
            enterGoal(input1, input2);
            //deposit dummy
            break;

        case 4:
            enterGoal(0, 0);
            //return to start needs tsome more logic made

            break;
        }

        Serial.println(operation);
        Serial.println(input1);
        Serial.println(input2);

        commands.toCharArray(ccommands, commands.length());

        command = strtok(ccommands, ".");

        i = 0;

        while (i < count) {
            command = strtok(0, ".");
            i++;
        }
    }

}
