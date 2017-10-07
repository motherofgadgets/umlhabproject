import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.output(16,GPIO.HIGH)
while True:
	GPIO.output(12,GPIO.HIGH)
	print "LED on"
	time.sleep(1)
	GPIO.output(12,GPIO.LOW)
	print "LED off"
	time.sleep(1)

