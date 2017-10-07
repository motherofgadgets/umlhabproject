import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
for i in range(0,15):
	a = i/2
	b = i%2
	if b==1:
		GPIO.output(22,GPIO.1)
	else:
		GPIO.output(22,GPIO.0)
	a = a/2
	b = a%2
	if b==1:
		GPIO.output(18,GPIO.1)
	else:
		GPIO.output(18,GPIO.0)
	a = a/2
	b = a%2
	if b==1:
		GPIO.output(16,GPIO.1)
	else:
		GPIO.output(16,GPIO.0)
	a = a/2
	b = a%2
	if b==1:
		GPIO.output(12,GPIO.1)
	else:
		GPIO.output(12,GPIO.0)

GPIO.cleanup()

