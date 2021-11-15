import urllib3
import keyboard

arduino = urllib3.PoolManager()
IP = ''

while True:
    if keyboard.is_pressed('1'):
        r = arduino.request('GET', 'http://%d/H'%IP)
        print(r.status)
        print(r.data)
    
    if keyboard.is_pressed('0'):
        r = arduino.request('GET', 'http://%d/L'%IP)
        print(r.status)
        print(r.data)
    
    if keyboard.is_pressed('q'):
        break


