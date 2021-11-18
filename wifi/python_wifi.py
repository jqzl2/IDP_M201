import random
import urllib3
import keyboard

arduino = urllib3.PoolManager()

while True:
    if keyboard.is_pressed('s'):
        lol = random.randint(0,240)
        r = arduino.request('GET', 'http://192.168.137.131/?lol=%d'%lol)
    
    if keyboard.is_pressed('q'):
        break


