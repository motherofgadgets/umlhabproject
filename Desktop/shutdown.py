from time import sleep
def shutdown():
	command = "/usr/bin/sudo /sbin/shutdown -h now"
	import subprocess
	process = subprocess.Popen(command.split(),stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print output

sleep(1320)

shutdown()
