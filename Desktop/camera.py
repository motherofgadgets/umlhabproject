from picamera import PiCamera
from time import sleep
camera = PiCamera()

for i in xrange ( 4 ) :
	filename = '/home/pi/Desktop/image'+str(i)+'.jpg'


	camera.start_preview()
	sleep(5)
	camera.capture(filename)
	camera.stop_preview()
