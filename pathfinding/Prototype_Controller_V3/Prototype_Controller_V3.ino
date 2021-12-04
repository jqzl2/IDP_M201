//including relevant libraries
#include <Adafruit_MotorShield.h>

#include "SharpIR.h"

#include <Servo.h>

#include <math.h>

#include <SPI.h>

#include <WiFiNINA.h>

#include <string.h>

//these are constants used for the driving
#define MaxPower 255
#define USOffset 5
#define IROffset 1
#define feedBackFactor 1

//these are constants used to make the wall distance function easier to read
#define X1 0.0
#define Y1 0.0
#define X2 - 10.0
#define Y2 0.0
#define X3 X1
#define X4 X2

//define the time to turn 90 degrees
#define RTurn 1000

//defining the numbers of the pins for the sensors etc
//IR Distance sensor pins, analog
#define IRPinS A3
#define IRPinF A2

//QSD IR transistor pins, analogue
#define qsdPin1 A0
#define qsdPin2 A1

//LED indicator pins, digital
#define redPin 2
#define greenPin 3
#define motorPin 4

//UltraSonic echo and trig pins, digital
#define echoPinFront 13
#define trigPinFront 12
#define echoPinSide 8
#define trigPinSide 11

//pin for the IR sensing TSOP, digital
#define tsopPin 5

//pin for the lin sensor return, digital
#define lineSensorPin 7

//wifi magic values for connecting to laptops
const char * ssid = "M201";
const char * password = "WacManIDP";
const uint16_t port = 8090;
IPAddress gateway;

//global variable declarations
long duration; // variable for the duration of sound wave travel
bool carrying = false; //is the robot carrying a dummy
bool collecting = false; //is the robot collecting a dummy

int tsop = 0; // variables to store values read, these are global to reduce the time spent in memory allocation during dummy differentation
int qsd1 = 0;
int qsd2 = 0;

int USDistance;
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

  // ensure that the motors start off neutral
  ML -> run(RELEASE);
  MR -> run(RELEASE);

  //attaching servos to correct ports
  leftServo.attach(9);
  rightServo.attach(10);

  //opening the door at the start
  openDoor();

  //start the wifi connection
  WiFi.begin(ssid, password);
  //while the connection is not yet working
  while (WiFi.status() != WL_CONNECTED) {
    //wait to try again
    delay(500);
    Serial.println("...");
  }

  //once the WiFi is connected set up the gateway and indiactor LED
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  gateway = WiFi.gatewayIP();
  digitalWrite(greenPin, HIGH);
}

// connect Arduino to Sockets server created on the PC
WiFiClient set_up_server() {
  WiFiClient client;
  //repeat this code untill a connection is succesful
  while (true) {
    //debugging prints
    if (!client.connect(gateway, port)) {
      Serial.println("Connection to host failed");
    } else {
      Serial.println("Connected to server successful!");
      //return the connected server
      return client;
    }
  }
}

// send dummy mode to server, and then receive the PC's next commands
String send_mode_receive_path(WiFiClient client, int mode) {
  String commands = "";
  client.print(mode);
  // if there are bytes to read from the client
  while (true) {
    if (client.available()) {
      // read a byte
      char c = client.read();
      //add it to the return string
      commands += c;
      //if its the terminating char then return
      if (c == '$') {
        return commands;
      }
    }
  }
  return commands;
}

//find the dummy mode using sensors
int dummyMode() {
  //read the QSD's
  qsd1 = analogRead(qsdPin1);
  qsd2 = analogRead(qsdPin2);

  int Mode = 0;
  // dummy signal detected (1 = 0.049mV)
  if (qsd1 > 200 || qsd2 > 200) {
    // 38kHz detected (1st cycle)
    tsop = digitalRead(tsopPin);
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
  if ((l != 0) or(r != 0)) {
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

  //reads the relevent 2 sensors
  int fDist = frontIR.distance();
  int uDist = readUltraSonic(trigPinFront, echoPinFront);

  //if the robot is moving a dummy or
  //if the robot is at the limits of the US sensor, and is not collecting
  if (carrying or(uDist > 70 and!collecting)) {
    //just use the IR sensor
    return fDist - IROffset;
  }

  //just use the US sensor
  return uDist - USOffset;
}

//returns the distance from the side of the vehical
int distanceSide() {
  //get the two distances
  IRDistance = sideIR.distance();
  USDistance = readUltraSonic(trigPinSide, echoPinSide);

  //this is all vectors, see https://www.desmos.com/calculator/k5fv7n715q for details
  //find the projected Y values, projected X values are the same as their parents
  float Y3 = Y1 - USDistance;
  float Y4 = Y2 - IRDistance;

  //P = -progected point from 1
  float P1 = -1 * X3;
  float P2 = -1 * Y3;

  //C = the difference between the 2 projected points 
  float C1 = X4 - X3;
  float C2 = Y4 - Y3;

  //t is equall to the % of C the closest point is between the 2 projected points
  float t = (P1 * C1) + (P2 * C2);
  t /= (C1 * C1) + (C2 * C2);

  //point 5 is the closest point on the line
  float X5 = X3 + (C1 * t);
  float Y5 = Y3 + (C2 * t);

  //returns the magnitude of point 5
  return pow((X5 * X5) + (Y5 * Y5), 0.5) + 10;
}

//24 , 24 base
//50 , 90 blue
//90 , 50 red
//24 , 24 white

//this code is identical to the goToDistance but uses the line sensor or time to terminate
//it is its own function in order to optimise for speed
void enterGoal(int mode, int sideGoal) {
  //setting up local variables
  int rightSpeed = MaxPower;
  int leftSpeed = MaxPower;
  float mult;
  float dt;

  //dt is the distance moved in 1 second
  dt = 10 * 3.14 * 40 / 60;

  //which type of goal is it
  switch (mode) {
  case 0:
  case 1:
    //move the correct distance into the goal from the correct distance away
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

  //convert dt into milliseconds
  dt *= 1000;
  int start = millis();

  //until dt milliseconds has passed, or a line has been found
  while (millis() - start < dt and digitalRead(lineSensorPin) == 0) {
    //maintain the correct distance
    adjustDrive(sideGoal, 1);
  }

  //hard-coded dummy deposit sequence
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
void goToDistanceWrapper(int goal, int sideGoal) {
  //if the robot is carrying a dummy
  if (carrying) {
    //this is called multiple times to account for the IR innacuracy
    goToDistance(goal + 30, sideGoal);
    goToDistance(goal + 30, sideGoal);
    goToDistance(goal + 30, sideGoal);
    goToDistance(goal + 30, sideGoal);
    goToDistance(goal + 30, sideGoal);
    goToDistance(goal + 30, sideGoal);
    //as the IR cant see under 30 cm the robot stops 30 cm from its goal then drives 30 cm
    maintainDistance(2000, sideGoal);
    drive(0, 0);

  } else {
    //this is called multiple times to account for the US innacuracy
    goToDistance(goal, sideGoal);
    goToDistance(goal, sideGoal);
    goToDistance(goal, sideGoal);
  }

  //if there has been a consistent error try again
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
    drive(255, 255);
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
  //turn clockwise or anticlockwise
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

  //make sure wheels always end neutral
  drive(0, 0);
  delay(500);
}

//opens the doors and sets carrying
void openDoor() {
  leftServo.write(30);
  rightServo.write(120);
  carrying = false;
}

//closes the doors and sets carrying
void closeDoor() {
  leftServo.write(90);
  rightServo.write(60);
  carrying = true;
}

//used to blindly drive forwards
int blindDrive(int dist, int sign) {
  //start driving
  drive(255 * sign, 255 * sign);

  //wait for the correct time to elapse
  //this assumes that the robot is moving at 20cm/s
  int start = millis();
  while ((millis() - start) < dist * 50) {
    delay(1);
  }

  //stop driving
  drive(0, 0);
  return millis() - start;

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

  //return mode
  return dummyMode;
}

//runtime loop
void loop() {
  //set up the wifi
  WiFiClient client = set_up_server();
  int mode = 0;
  //once wifi is set up repeat forever
  while (true) {
    //get the commands
    String commands;
    String request = send_mode_receive_path(client, mode);

    //human debugging LED
    digitalWrite(redPin, HIGH);

    //seperate the input by the !'s giving a valid instruction string
    char * crequest = new char[request.length() + 1];
    strcpy(crequest, request.c_str());
    char * data = strtok(crequest, "!");

    int i = 0;
    //the instruction string is the second piece of data
    while (data != 0 && i < 4) {
      i += 1;
      data = strtok(NULL, "!");
      if (i == 1) {
        commands = data;
        break;
      }
    }
    //memory cleanup
    delete[] crequest;

    int count = 0;
    char * ccommands = new char[commands.length() + 1];
    //strcpy(ccommands, commands.c_str());

    //start to seperate the command string into individual commands
    commands.toCharArray(ccommands, commands.length());
    char * command = strtok(ccommands, ".");

    count = 0;

    //while there is some new command
    while (command != 0) {
      //add to the number of commands executed
      count += 1;

      //get the next instruction
      String parsingArray = strtok(command, ",");

      //get the 3 components of it
      int operation = parsingArray.toInt(); // mode, always used
      parsingArray = strtok(0, ",");

      int input1 = parsingArray.toInt(); // first set of data, always used

      parsingArray = strtok(0, ",");
      int input2 = parsingArray.toInt(); // second set, often not used

      //dealing with the operators
      switch (operation) {
      //go to distance from wall with normal wall following
      case 0:
        goToDistanceWrapper(input1, input2);
        break;

      //turn input1 * 90degrees clockwise
      case 1:
        turnOnSpot(input1 * -1);
        break;

      //collect the dummy and get the mode ready for return
      case 2:
        goToDistance(0, input1);
        mode = collectDummy(input1);
        break;

      //deposit the dummy in its goal
      case 3:
        enterGoal(input1, input2);
        break;

      //enter the start goal
      case 4:
        enterGoal(0, 0);
        break;

      //blindly drive forward, worst case pathing scenario
      case 5:
        drive(255, 255);
        delay(input1 * 50);
        drive(0, 0);
        break;

      //go input1 cm forward while following the wall
      case 6:
        maintainDistance(input1 * 50, input2);
        break;

      //debugging case
      case 7:
        openDoor();
        delay(5000);
        closeDoor();
        delay(5000);
        break;
      }

      //reset the char array to parse the next instruction, done due to how strtok works
      commands.toCharArray(ccommands, commands.length());
      command = strtok(ccommands, ".");

      i = 0;
      //read the next instruction untill the next command will be the next one to be executed
      while (i < count) {
        command = strtok(0, ".");
        i++;
      }
    }
  }
}