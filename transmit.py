def transmit():
	command = "usr/bin/sudo php aprs-position-beacon.php"
	import subprocess
	process = subprocess.Popen(command.split(),stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output

transmit()

