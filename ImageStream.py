import urllib.request
import PIL.Image
import os




f = urllib.request.urlretrieve('http://localhost:8081/stream', 'video.mjpeg')
f = urllib.request.urlopen('http://localhost:8081/stream/video.mjpeg')
print(f)

print(f.read(1000))
#image = PIL.Image.open(urllib.request.urlretrieve('http://localhost:8081/stream', 'video.mjpeg'))