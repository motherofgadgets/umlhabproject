import numpy as np
import math
from math import pi

import time
import threading
from threading import Timer
from threading import Thread
from Queue import Queue

import RPi.GPIO as GPIO
import picamera
from sense_hat import SenseHat



from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor

import time
import atexit


sense = SenseHat()


#===================================================================
#			Pulling Misc Data 
#===================================================================

def sensor():

    while True:
        pitch, roll, yaw = sense.get_orientation().values()
        t = sense.get_temperature()
        p = sense.get_pressure()
        h = sense.get_humidity()
        data2 = [t,p,h]


t2 = Thread(target=sensor, args=())
t2.start()


#===================================================================
#			LIGHTS. CAMERA. ACTION!
#===================================================================
#We're going to thread this action as I want the script to stop upon retrieval

FRAMES = 3

def capture_frame(frame):
    with picamera.PiCamera() as cam:
        with picamera.array.PiYUVArray(cam) as output:
            cam.framerate = Fraction(1,6)
            cam.shutter_speed = 6000000
            cam.exposure_mode = 'off'
            cam.iso = 800
            time.sleep(2)
            cam.capture(output, 'yuv')
            print('Captured %dx%d image' % (
                output.array.shape[1], output.array.shape[0]))
            yuv = np.array([output.array[0:(output.array.shape[0])]])
            index = yuv[0,0:1920,0:1080,0]
            np.savetxt('/home/pi/Desktop/Launch/expo_6sec%03d.txt' % frame, index)

# Capture the images
def camera():
    for frame in range(FRAMES):
        # Note the time before the capture
        start = time.time()
        capture_frame(frame)
        time.sleep(3)


t1 = Thread(target=camera, args=())
t1.start()

#===================================================================
#			Responsive Stepper Motor 
#===================================================================

#Here we will consume data from the senseHAT and convey it to the stepper motor as to tell it how to orient itself. 
# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x61)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

myStepper = mh.getStepper(513, 1)       # 513 steps/rev, motor port #1

myStepper.setSpeed(25)  #RPM advised to keep this <25 for 32 stepper

#Pull Information

dir0 = sense.get_compass()

halfmax = int(513/2) #Midway point of 32 Stepper Motor
degstep = 0.701754386 #(360/513) Step/degree 

while True:
    #print"initial", yaw0
    #time.sleep(1)
    dir1 = sense.get_compass()
    #print"yaw1", yaw1
    dif = dir0 - dir1
    #steps = abs(steps - halfmax) 
    if dif > 0 and dif <= 180:
        print"degrees(dif)", dif
        steps = abs(int(dif/degstep))
        print"Forward", steps, "steps"
        myStepper.step(steps, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE)
    if  dif < 0 and dif >= -180: 
        deg = 360 - abs(dif)
        print"dif", dif
        print"degrees",deg
        steps = (int(deg/degstep)) 
        #steps = abs(steps - halfmax)
        print"Backward", steps, "steps"
        myStepper.step(steps, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE)
    #time.sleep(0.5)


#And that's all she wrote!

