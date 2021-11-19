#include <Adafruit_MotorShield.h>

#include <SharpIR.h>

#include <Servo.h.

#define IRPinF A1
#define IRPinS A0

#define echoPinFront 4 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPinFront 5 //attach pin D3 Arduino to pin Trig of HC-SR04

#define echoPinSide 8
#define trigPinSide 9

#define motorPin 7

#define MaxPower 255

#define X1 0.0
#define Y1 0.0

#define X2 - 10.0
#define Y2 0.0

#define X3 X1
#define X4 X2

#define RTurn 0.8625

#define tsopPin 6
#define qsdPin1 A2
#define qsdPin2 A3

#define redPin 1
#define greenPin 2



// defines variables
long duration; // variable for the duration of sound wave travel
int distance; // variable for the distance measurement

int tsop = 0; // variable to store the value read
int qsd1 = 0;
int qsd2 = 0;

// Create the motor shield object with the default I2C address

Adafruit_MotorShield AFMS = Adafruit_MotorShield();
SharpIR frontIR = SharpIR(IRPinF, 20150);

int USDistance; // variable for the distance measurement
int IRDistance;

SharpIR sideIR = SharpIR(IRPinS, 1080);

// Select which 'port' M1, M2, M3 or M4. In this case, M1

Adafruit_DCMotor * ML = AFMS.getMotor(1);
Adafruit_DCMotor * MR = AFMS.getMotor(2);

void setup() {
    Serial.begin(9600); // set up Serial library at 9600 bps
    Serial.println("Adafruit Motorshield v2 - DC Motor test!");

    if (!AFMS.begin()) { // create with the default frequency 1.6KHz
        Serial.println("Could not find Motor Shield. Check wiring.");
        while (1);
    }
    Serial.println("Motor Shield found.");

    // Set the speed to start, from 0 (off) to 255 (max speed)

    ML -> run(RELEASE);
    MR -> run(RELEASE);

    pinMode(trigPinFront, OUTPUT); // Sets the trigPin as an OUTPUT
    pinMode(echoPinFront, INPUT); // Sets the echoPin as an INPUT
    pinMode(trigPinSide, OUTPUT); // Sets the trigPin as an OUTPUT
    pinMode(echoPinSide, INPUT); // Sets the echoPin as an INPUT
    pinMode(motorPin, OUTPUT);

}

int dummyMode() {
    qsd1 = analogRead(qsdPin1);
    qsd2 = analogRead(qsdPin2);

    int Mode = 0;

    //Serial.println((String)"tsop:" + tsop);          // debug value
    //Serial.println((String)"qsd1:" + qsd1);
    //Serial.println((String)"qsd2:" + qsd2);

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

            //cycle_a1 = micros();    //time ends
            //Serial.print("cycle time: ");
            //Serial.println(cycle_a1-cycle_a);

            if (tsop == 0) {
                //Serial.println((String)"Mode 1 - 11");     // Mode = 1
                Mode = 1;
                // set R and G LED on
                // 38kHz not detected (2nd cycle)
            } else {
                //Serial.println((String)"Mode 3 - 12");     // Mode = 3
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
            //cycle_b = micros();

            // phase difference! 38kHz detected (1st cycle)
            if (tsop == 0) {
                // 38kHz detected (2nd cycle)
                delay(6);
                tsop = digitalRead(tsopPin);
                //cycle_b1 = micros();     //time ends
                //Serial.print("cycle time: ");
                //Serial.println(cycle_b1-cycle_b);
                if (tsop == 0) {
                    //Serial.println((String)"Mode 1 - 21");   // Mode = 1
                    Mode = 1;
                    // set R and G LED on
                }
                // 38kHz not detected (2nd cycle)
                else if (tsop == 1) {
                    //Serial.println((String)"Mode 3 - 22");   // Mode = 3
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
                //cycle_b2 = micros();
                //Serial.print("cycle time: ");
                //Serial.println(cycle_b2-cycle_b);

                // 38kHz undetected (2nd)
                if (tsop == 1) {
                    //Serial.println((String)"Mode 2 - 31");   // Mode = 2
                    Mode = 2;
                    // set R LED on
                }
                // 38kHz detected (2nd)
                else {
                    //Serial.println((String)"Mode 3 - 32");   // Mode = 3
                    Mode = 3;
                    // set G LED on
                }
            }
        }
    }
    return Mode;
}

int DiffDummy() {
    int mode_sum = 0;
    int count = 100;
    int mode = 0;
    while (count != 0) {
        mode = dummyMode();
        if (mode != 0) {
            mode_sum += mode - 2;
            count -= 1;
        }

    }
    //Serial.println(mode_sum);

    // adjust the threshold value to change accuracy
    if (mode_sum > 50) {
        //Serial.println("Mode is");
        return 3;
    } else if (mode_sum < -50) {
        //Serial.println("Mode is");
        return 1;
    } else {
        //Serial.println("Mode is");
        return 2;
    }

    delay(1);
}

void drive(int l, int r) {
    if (l < 0) {
        ML -> run(BACKWARD);
    } else {
        ML -> run(FORWARD);
    }

    if (r < 0) {
        MR -> run(BACKWARD);
    } else {
        MR -> run(FORWARD);
    }

    ML -> setSpeed(abs(l));
    MR -> setSpeed(abs(r));

    if ((l != 0) or(r != 0)) {
        digitalWrite(motorPin, HIGH);
    } else {
        digitalWrite(motorPin, LOW);
    }
}

int readUltraSonic(int pulse, int returnPin) {
    digitalWrite(pulse, LOW);
    delayMicroseconds(2);

    digitalWrite(pulse, HIGH);
    delayMicroseconds(10);
    digitalWrite(pulse, LOW);

    duration = pulseIn(returnPin, HIGH);

    return (duration * 0.034 / 2);
}

int distanceFront() {
    USDistance = frontIR.distance();

    USDistance = readUltraSonic(trigPinFront, echoPinFront);
    return USDistance;
}

int distanceSide() {
    IRDistance = sideIR.distance();
    USDistance = readUltraSonic(trigPinSide, echoPinSide);

    Serial.println(IRDistance);
    Serial.println(USDistance);
    Serial.println("");
    Serial.println("");

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

    return pow((X5 * X5) + (Y5 * Y5), 0.5);
}

void goToDistance(int goal, int sideGoal) {

    int rightSpeed = MaxPower;
    int leftSpeed = MaxPower;
    int sign = 1;
    float feedBackFactor = 1;

    if (goal > distanceFront()) {
        sign = -1;
    }

    rightSpeed *= sign;
    leftSpeed *= sign;

    drive(rightSpeed, leftSpeed);

    float t1 = millis();
    float dt, t2;
    float mult;

    while (sign * distanceFront() > sign * goal) {

        mult = (float) distanceSide() / (float) sideGoal;
        mult = 1 - mult;

        mult *= feedBackFactor;

        if (mult < 0) {
            rightSpeed = MaxPower * (1 + mult);
            leftSpeed = MaxPower;
        } else {
            leftSpeed = (1 - mult) * MaxPower;
            rightSpeed = MaxPower;
        }

        leftSpeed *= sign;
        rightSpeed *= sign;

        drive(rightSpeed, leftSpeed);

        Serial.println(distanceFront());
        Serial.println(distanceSide());
        Serial.println(rightSpeed);
        Serial.println(leftSpeed);
        Serial.println(mult);
        Serial.println("");
    }

    drive(0, 0);
    delay(1000);
}

void turnCorner(int sign) {
    if (sign > 0) {
        drive(255, 75);
    } else {
        drive(75, 255);
    }
    delay(2000);
    drive(0, 0);
}

void turnOnSpot(int n) {
    if (n > 0) {
        drive(255, -255);
    } else {
        drive(-255, 255);
    }

    delay(abs(n) * RTurn);

    drive(0, 0);
}

void loop() {
    Serial.println(DiffDummy());
    Serial.println("");
    delay(100);
}
