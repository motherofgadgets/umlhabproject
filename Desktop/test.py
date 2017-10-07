# Test Code
from time import sleep

try:
	while True:
		f=open('/home/pi/Desktop/output.txt','w')
		f.write("Hello World"+" "+"This is a test")
		f.write('\n')
		sleep(1)
	f.close()

except KeyboardInterrupt, e:
	Logging.info("Stopping...")
