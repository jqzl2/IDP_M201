import urllib3
import keyboard
import random
import json

arduino = urllib3.PoolManager()

while True:
    if keyboard.is_pressed('s'):
        coord = (random.randint(0,240), random.randint(0,240))
        angle = random.randint(0,360)
        data = {'position': coord, 'orientation': angle}
        encoded_data = json.dumps(data).encode('utf-8')
        r = arduino.request('PUT', 'http://192.168.137.168/', body = encoded_data, headers = {'Content-Type': 'application/json'})

        json.loads(r.data.decode('utf-8'))['json']

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


