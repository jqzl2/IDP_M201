import urllib3
import keyboard

arduino = urllib3.PoolManager()

while True:
    if keyboard.is_pressed('1'):
        r = arduino.request('GET', 'http://192.168.137.235/H')
        print(r.status)
        print(r.data)
    
    if keyboard.is_pressed('0'):
        r = arduino.request('GET', 'http://192.168.137.235/L')
        print(r.status)
        print(r.data)
    
    if keyboard.is_pressed('q'):
        break


