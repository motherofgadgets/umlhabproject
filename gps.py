def gps():
	command = "/usr/bin/sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock"
	import subprocess
	process = subprocess.Popen(command.split(),stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output

gps()

