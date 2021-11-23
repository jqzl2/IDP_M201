import random
import urllib3
import keyboard

# arduino = urllib3.PoolManager()

# while True:
#     if keyboard.is_pressed('s'):
#         data = random.randint(0,240)
#         r = arduino.request('GET', 'http://192.168.137.254/?lol=%d'%data)
    
#     if keyboard.is_pressed('q'):
#         break


def send_data(ip,data):
    arduino = urllib3.PoolManager()
    r = arduino.request('GET', 'http://%e/?data=%d'%ip%data)
    r.status
    r.data