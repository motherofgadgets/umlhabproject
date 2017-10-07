from picamera import PiCamera
from time import sleep
cam = PiCamera()

for i in xrange ( 2 ) :
	filename = '/home/pi/Desktop/image'+str(i)+'.jpg'

	cam.start_preview()
	sleep(2)
	#cam.framerate = Fraction(1,2)
	cam.shutter_speed = 2000000
	cam.exposure_mode = 'off'
	cam.iso = 800
	sleep(2)
	cam.capture(filename)
	cam.stop_preview()



