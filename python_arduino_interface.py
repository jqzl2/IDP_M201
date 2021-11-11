import serial #Serial imported for Serial communication
import time #Required to use delay functions

ArduinoSerial = serial.Serial('com18',9600)
time.sleep(2)
print(ArduinoSerial.readline())

ArduinoSerial.write('1')

