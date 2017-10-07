from picamera import PiCamera
from time import sleep
from time import time

camera = PiCamera()
camera.start_recording('/home/pi/Desktop/'+str(time())+'.h264')
sleep(1200)
camera.stop_recording()

