import serial #Serial imported for Serial communication
import time #Required to use delay functions
import keyboard

arduino = serial.serial_for_url("http://192.168.137.72/")
time.sleep(2)

while True:
    if keyboard.is_pressed('1'):
        arduino.write(str.encode('1'))
        print("LED is ON")
        time.sleep(1)

    if keyboard.is_pressed('0'):
        arduino.write(str.encode('0'))
        print("LED is OFF")
        time.sleep(1)
    
    if keyboard.is_pressed('q'):
        break
