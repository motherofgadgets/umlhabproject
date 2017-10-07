import picamera
import picamera.array
import numpy as np
import math
from fractions import Fraction
from math import pi
import time
import threading
from threading import Timer
from threading import Thread
from Queue import Queue

FRAMES = 3

def capture_frame(frame):
	with picamera.PiCamera() as cam:
		with picamera.array.PiYUVArray(cam) as output:
			cam.framerate = Fraction(1,6)
			cam.shutter_speed = 6000000
			cam.exposure_mode = 'off'
			cam.iso = 800
			time.sleep(2)
			cam.capture(output,'yuv')
			print('Captured %d%d image' % (output.array.shape[1],output.array.shape[0]))
			yuv = np.array([output.array[0:(output.array.shape[0])]])
			index = yuv[0,0:1920,0:1080,0]
			np.savetxt('/home/pi/Desktop/expo_6sec%3d'+str(time())+'.txt' % frame, index)

# Capture the images
def camera():
	for frame in range(FRAMES):
		start = time.time()
		capture_frame(frame)
		time.sleep(3)

t1 = Thread(target=camera,args=())
t1.start()
