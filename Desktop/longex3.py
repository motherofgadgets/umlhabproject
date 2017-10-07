from picamera import PiCamera
from time import sleep
from fractions import Fraction

camera = PiCamera(resolution=(1280,720),framerate_range=(Fraction(1,6),Fraction(1,2)),sensor_mode=3)
camera.shutter_speed = 2000000
camera.iso = 500
sleep(6)
camera.exposure_mode='off'
camera.capture('/home/pi/Desktop/dark.jpg')

