#include <Adafruit_MotorShield.h>

#include <SharpIR.h>

#include <Servo.h>

#define MaxPower 255
#define USOffset 5
#define IROffset 1

#define X1 0.0
#define Y1 0.0

#define X2 -10.0
#define Y2 0.0

#define X3 X1
#define X4 X2

#define RTurn 862

#define IRPinS A0
#define IRPinF A1

#define qsdPin1 A2
#define qsdPin2 A3

#define redPin 2
#define greenPin 3

#define echoPinFront 4 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPinFront 5 //attach pin D3 Arduino to pin Trig of HC-SR04

#define tsopPin 6
#define motorPin 7
#define lineSensorPin 8

#define echoPinSide 11
#define trigPinSide 12


//pins 8 is free
//analog 4 is free

//global variable deffinition
long duration; // variable for the duration of sound wave travel
bool carrying = false; //is the robot carrying a dummy

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
    leftServo.attach(10);
    rightServo.attach(9);

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

    return (duration * 0.034 / 2);
}

//returns the distance from the front of the vehical
int distanceFront() {

    if (carrying) {
        return frontIR.distance() - IROffset;
    }
    return readUltraSonic(trigPinFront, echoPinFront) - USOffset;
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

    float C1 = X4 - X3;0
    float C2 = Y4 - Y3;

    float t = (P1 * C1) + (P2 * C2);
    t /= (C1 * C1) + (C2 * C2);

    float X5 = X3 + (C1 * t);
    float Y5 = Y3 + (C2 * t);

    return pow((X5 * X5) + (Y5 * Y5), 0.5);
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
    float feedBackFactor = 1;
    float mult;
    float dt;

    int distnaces[4] = {
        24,
        50,
        90,
        24
    };

    dt = 10 * 3.14 * 40 / 60;

    switch (mode) {
    case 0:
    case 3:
        dt *= 24;
        break;

    case 1:
        dt *= 50;
        break;

    case 2:
        dt *= 90;
        break;
    }

    dt *= 1000;
    int start = millis();

    while (millis() - start < dt and digitalRead(lineSensorPin) == 0) {

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

    //make sure wheels always end neutral
    drive(0, 0);
}

//general movement code
void goToDistance(int goal, int sideGoal) {

    //setting up local variables
    int rightSpeed = MaxPower;
    int leftSpeed = MaxPower;
    int sign = 1;
    float feedBackFactor = 1;
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
    }

    //make sure wheels always end neutral
    drive(0, 0);
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
    delay((int)(abs(n) * 1200));

    //make sure wheels always end neutral
    drive(0, 0);
}

void openDoor() {
    //open door
    leftServo.write(30);
    rightServo.write(120);
    carrying = false;
}

void closeDoor() {
    leftServo.write(75);
    rightServo.write(75);
    carrying = true;
}

int collectDummy() {

    openDoor();

    //get close to dummy
    goToDistance(0, distanceSide());


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

    delay(5555);[

    drive(255,255);
    delay(238);
    drive(0,0);

    //close doors

    closeDoor();

    //return mode
    return dummyMode;
}

void loop() {

  goToDistance(10,10);
  turnOnSpot(1);
  

}
