import random
import urllib3
import keyboard

arduino = urllib3.PoolManager()

while True:
    if keyboard.is_pressed('s'):
        lol = random.randint(0,240)
        r = arduino.request('GET', 'http://192.168.137.131/?lol=%d'%lol)

    # if keyboard.is_pressed('1'):
    #     r = arduino.request('GET', 'http://192.168.137.217/H')
    #     print(r.status)
    #     print(r.data)
    
    # if keyboard.is_pressed('0'):
    #     r = arduino.request('GET', 'http://192.168.137.217/L')
    #     print(r.status)
    #     print(r.data)
    
    if keyboard.is_pressed('q'):
        break


