#include <Adafruit_MotorShield.h>

#include "SharpIR.h"

#include <Servo.h>

#include <math.h>

#include <SPI.h>

#include <WiFiNINA.h>

#include <string.h>

#define MaxPower 255
#define USOffset 5
#define IROffset 1
#define feedBackFactor 1

#define X1 0.0
#define Y1 0.0

#define X2 - 10.0
#define Y2 0.0

#define X3 X1
#define X4 X2

//#define RTurn 825
#define RTurn 1000

#define IRPinS A3
#define IRPinF A2

#define qsdPin1 A0
#define qsdPin2 A1

#define redPin 2
#define greenPin 3

#define echoPinFront 13 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPinFront 12 //attach pin D3 Arduino to pin Trig of HC-SR04

#define tsopPin 5
#define motorPin 4
#define lineSensorPin 7

#define echoPinSide 8
#define trigPinSide 11

const char* ssid = "M201"; // your network SSID (name)
const char* password = "WacManIDP"; // your network password (use for WPA, or use as key for WEP)

const uint16_t port = 8090;
//const char * host = "0.0.0.0";
IPAddress gateway;

//pins 8 is free
//analog 4 is free

//global variable deffinition
long duration; // variable for the duration of sound wave travel
bool carrying = false; //is the robot carrying a dummy
bool collecting = false;

int tsop = 0; // variable to store the value read
int qsd1 = 0;
int qsd2 = 0;

int USDistance; //variabled for the distance measurementd
int IRDistance;

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

//attach 2 motors to variables
Adafruit_DCMotor * ML = AFMS.getMotor(1);
Adafruit_DCMotor * MR = AFMS.getMotor(2);

//setting up the IR distnace sensors
SharpIR frontIR = SharpIR(IRPinF, 20150);
SharpIR sideIR = SharpIR(IRPinS, 1080);

//setting up the servos globally
Servo leftServo, rightServo;

void setup() {
  //starting serial port
  Serial.begin(9600); // set up Serial library at 9600 bps

  //setting up digital pins
  pinMode(trigPinFront, OUTPUT);
  pinMode(echoPinFront, INPUT);
  pinMode(trigPinSide, OUTPUT);
  pinMode(echoPinSide, INPUT);
  pinMode(motorPin, OUTPUT);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(lineSensorPin, INPUT);

  //debug prints for motor shield
  Serial.println("Adafruit Motorshield v2 - DC Motor test!");
  if (!AFMS.begin()) { // create with the default frequency 1.6KHz
    Serial.println("Could not find Motor Shield. Check wiring.");
    digitalWrite(redPin, HIGH);
    while (1);
  }

  digitalWrite(redPin, LOW);
  Serial.println("Motor Shield found.");

  // Set the speed to start, from 0 (off) to 255 (max speed)
  ML -> run(RELEASE);
  MR -> run(RELEASE);

  //attaching servos to correct ports
  leftServo.attach(9);
  rightServo.attach(10);

  openDoor();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }

  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  gateway = WiFi.gatewayIP();
  digitalWrite(greenPin, HIGH);
}

WiFiClient set_up_server() {    // connect Arduino to Sockets server created on the PC (improvement: make client a global variable by declaring before void setup() i.e. outside of any function)
  WiFiClient client;
  while (true) {
    if (!client.connect(gateway, port)) {
      Serial.println("Connection to host failed");
    }

    else {
      Serial.println("Connected to server successful!");
      return client;
    }
  }
}

String send_mode_receive_path(WiFiClient client, int mode) {     // send dummy mode to server, and then receive the PC's next commands
  String commands = "";
  client.print(mode);
  while (true) { // if there are bytes to read from the client
    if (client.available()) {

      char c = client.read();   // read a byte
      //client.print(c);          // then print it out the serial monitor
      commands += c;
      if (c == '$') {
        return commands;                  // end of command signposted by '$', so stop trying to read incoming data from PC
      }
    }

    //command = "";    // clear command line
    //client.stop();
    //delay(10000);
  }
  return commands;
}

int dummyMode() {
  qsd1 = analogRead(qsdPin1);
  qsd2 = analogRead(qsdPin2);

  int Mode = 0;
  ///*
  // dummy signal detected (1 = 0.049mV)
  if (qsd1 > 200 || qsd2 > 200) {
    // 38kHz detected (1st cycle)
    tsop = digitalRead(tsopPin);
    //cycle_a = micros();     //time begins

    if (tsop == 0) {

      // 38kHz detected (2nd cycle)
      delay(6); //wait for 6ms to take cycle2 reading
      tsop = digitalRead(tsopPin);

      if (tsop == 0) {
        // Mode = 1
        Mode = 1;
        // 38kHz not detected (2nd cycle)
      } else {
        // Mode = 3
        Mode = 3;
        // set G LED on
      }
    }

    // 38kHz not detected (1st cycle) - examine if due to phase difference
    else if (tsop == 1) {
      int t = 0; // t starts when intensity detected
      do {
        tsop = digitalRead(tsopPin);
        t++; // check if tsop falls
      } while (t <= 7 && tsop == 1);

      // phase difference! 38kHz detected (1st cycle)
      if (tsop == 0) {
        // 38kHz detected (2nd cycle)
        delay(6);
        tsop = digitalRead(tsopPin);
        //time ends
        if (tsop == 0) {
          // Mode = 1
          Mode = 1;
          // set R and G LED on
        }
        // 38kHz not detected (2nd cycle)
        else if (tsop == 1) {
          // Mode = 3
          Mode = 3;
          // set G LED on
        }
      }

      // 38kHz not detected (1st cycle) - not due to phase difference
      else {
        delay(6); // wait for 5ms and check for a duration of 1ms
        int i = 0; // t starts when intensity detected
        do {
          tsop = digitalRead(tsopPin);
          i++; // check if tsop falls
        } while (i <= 10 && tsop == 1);

        // 38kHz undetected (2nd)
        if (tsop == 1) {
          // Mode = 2
          Mode = 2;
          // set R LED on
        }
        // 38kHz detected (2nd)
        else {
          // Mode = 3
          Mode = 3;
          // set G LED on
        }
      }
    }
  }
  return Mode;
}

int DiffDummy() {
  //setting up loop variables
  int mode_sum = 0;
  int count = 100;
  int mode = 0;

  //test signal 100 times
  while (count != 0) {
    mode = dummyMode();
    //if no dumm was detected try again
    if (mode != 0) {
      mode_sum += mode - 2;
      count -= 1;
    }

  }

  // adjust the threshold value to change accuracy
  if (mode_sum > 50) {
    return 3;
  } else if (mode_sum < -50) {
    return 1;
  } else {
    return 2;
  }
}

//generic controll for motors abstrating the specifics
void drive(int l, int r) {
  //if left is backwards
  if (l < 0) {
    ML -> run(BACKWARD);
  } else {
    ML -> run(FORWARD);
  }

  //if right is backwards
  if (r < 0) {
    MR -> run(BACKWARD);
  } else {
    MR -> run(FORWARD);
  }

  //set the correct speeds
  ML -> setSpeed(abs(l));
  MR -> setSpeed(abs(r));

  //start/stop blinking LED
  if ((l != 0) or (r != 0)) {
    digitalWrite(motorPin, HIGH);
  } else {
    digitalWrite(motorPin, LOW);
  }
}

//generic code to read an ultrasonic distance sensor
int readUltraSonic(int pulse, int returnPin) {

  //this code is generic for the model
  digitalWrite(pulse, LOW);
  delayMicroseconds(2);
  digitalWrite(pulse, HIGH);
  delayMicroseconds(10);
  digitalWrite(pulse, LOW);

  duration = pulseIn(returnPin, HIGH);
  if (duration) {
    return (duration * 0.034 / 2);
  }
  return 240;
}

//returns the distance from the front of the vehical
int distanceFront() {

  int fDist = frontIR.distance();
  int uDist = readUltraSonic(trigPinFront, echoPinFront);

  //if the robot is moving a dummy or
  //if the robot is at the limits of the US sensor, and is not collecting
  if (carrying or (uDist > 70 and !collecting)) {
    //just use the IR sensor
    return fDist - IROffset;
  }

  //just use the US sensor
  return  uDist - USOffset;
}



//returns the distance from the side of the vehical
int distanceSide() {
  //get the two distances
  IRDistance = sideIR.distance();
  USDistance = readUltraSonic(trigPinSide, echoPinSide);

  //this is all vectors, see https://www.desmos.com/calculator/k5fv7n715q for details
  float Y3 = Y1 - USDistance;
  float Y4 = Y2 - IRDistance;

  float P1 = -1 * X3;
  float P2 = -1 * Y3;

  float C1 = X4 - X3;
  float C2 = Y4 - Y3;

  float t = (P1 * C1) + (P2 * C2);
  t /= (C1 * C1) + (C2 * C2);

  float X5 = X3 + (C1 * t);
  float Y5 = Y3 + (C2 * t);

  return pow((X5 * X5) + (Y5 * Y5), 0.5) + 10;
}

//this returns the angle between the robot and the wall, used for turning
float angleSide() {
  //get the two distances
  IRDistance = sideIR.distance();
  USDistance = readUltraSonic(trigPinSide, echoPinSide);

  //this is all vectors, see https://www.desmos.com/calculator/k5fv7n715q for details
  float Y3 = Y1 - USDistance;
  float Y4 = Y2 - IRDistance;

  float P1 = -1 * X3;
  float P2 = -1 * Y3;

  float C1 = X4 - X3;
  float C2 = Y4 - Y3;

  float t = (P1 * C1) + (P2 * C2);
  t /= (C1 * C1) + (C2 * C2);

  float X5 = X3 + (C1 * t);
  float Y5 = Y3 + (C2 * t);

  if (X5 < 0) {
    return 1.0;
  }

  return -1.0;

  return atan(X5 / Y5);
}

//24 base
//50 blue
//90 red
//24 white

//this code is identical to the goToDistance but uses the line sensor or time to terminate
//it is its own function in order to optimise for speed
void enterGoal(int mode, int sideGoal) {
  //setting up local variables
  int rightSpeed = MaxPower;
  int leftSpeed = MaxPower;
  float mult;
  float dt;

  dt = 10 * 3.14 * 40 / 60;

  switch (mode) {
    case 0:
    case 1:
      dt *= 24;
      sideGoal = 24;
      break;

    case 2:
      dt *= 50;
      sideGoal = 90;
      break;

    case 3:
      dt *= 90;
      sideGoal = 50;
      break;
  }

  dt *= 1000;
  int start = millis();

  while (millis() - start < dt and digitalRead(lineSensorPin) == 0) {

    adjustDrive(sideGoal, 1);
  }

  drive(255, 255);
  delay(1000);
  openDoor();
  drive(-255, -255);
  delay(1000);

  //make sure wheels always end neutral
  drive(0, 0);
}

// this is a wrapper to deal with the carrying logic
// the robot does each goTo multiple times to account for bad sensor reads
void goToDistanceWrapper (int goal, int sideGoal) {
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

  while (millis() - start < deltaTime) {
    drive(255,255);
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
  //while (angleSide() < 0) {
    //delay(1);
  //}

  //make sure wheels always end neutral
  drive(0, 0);
  delay(500);
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



int blindDrive(int dist, int sign) {
  drive(255 * sign, 255 * sign);
  int start = millis();
  while ((millis() - start) < dist * 50) {
    delay(1);
  }
  return millis() - start;
  drive(0, 0);
}

void goToGoal(int mode) {
  turnOnSpot(-1);
  int sign = 1;
  if (distanceFront() < 5) {
    sign = -1;
  }

  blindDrive(5, sign);
  turnOnSpot(1);

  //should now be aligned with back right wall

  if (mode == 1) {
    maintainDistance(1000, 15);
    drive(255, 255);
    delay(1000);
    drive(0, 0);

    turnOnSpot(2);

    openDoor();

    drive(-255, -255);

    delay(1000);

    turnOnSpot(-2);

    goToDistanceWrapper(5, 15);
    turnOnSpot(1);
  } else {
    goToDistanceWrapper(5, 15);
    turnOnSpot(1);

    goToDistanceWrapper(70, 5);

    if (mode == 2) {
      goToDistanceWrapper(30, 5);
    }

    turnOnSpot(1);

    enterGoal(mode , 1);

    drive(-255, -255);
    delay(1000);

    turnOnSpot(-1);
  }

  goToDistanceWrapper(5, 15);
  turnOnSpot(1);
}


//dummy collection logic
int collectDummy(int dummySide) {
  //special mode used to force the robot to use the US sensor
  collecting = true;

  //ensures that the doors are open
  openDoor();

  //get close to dummy
  //goToDistance(0, dummySide);
  goToDistanceWrapper(0, dummySide);

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
  delay(350);
  drive(0, 0);

  //close doors

  closeDoor();

  //back to default mode handling
  collecting = false;

  //goToGoal(dumm yMode);

  //return mode
  return dummyMode;
}

void loop() {
  WiFiClient client = set_up_server();
  int mode = 0;
  while(true){
  String commands;
  String request = send_mode_receive_path(client, mode);
  digitalWrite(redPin, HIGH);
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
        turnOnSpot(input1 * -1);
        //turn on spot
        break;

      case 2:

        goToDistance(0, input1);

        mode =   collectDummy(input1);

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

       case 5:
         drive(255,255);
         delay(input1 * 50);
         drive(0,0);
         break;

       case 6:
         maintainDistance(input1 * 50 , input2);
         break;

       case 7:
          openDoor();
          delay(5000);
          closeDoor();
          delay(5000);
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
  digitalWrite(redPin, LOW);
}
