# aprs.py
#
# by Danae Moss
#
# This script runs indefinitely, receiving GPS coordinates through a queue from the position script
# It then converts the data to APRS format, creates an APRS soundfile and broadcasts
#
# This script is adapted for Python from Super Simple APRS Position Reporter by Midnight Cheese
# http://midnightcheese.com/2015/12/super-simple-aprs-position-beacon/
#

from subprocess import call
import threading

CALLSIGN = "KC1HZL-7"  # Do NOT change this variable! We are registered for this callsign
COMMENT = "UML HAB Nav Test"  # This variable can be changed. Goes out in message field of APRS string
SOUNDFILE = "packet.wav"


class Aprs(threading.Thread):
    # Initiates an instance of itself as a thread, sets to running
    def __init__(self, aprs_queue):
        threading.Thread.__init__(self)
        self.aprs_queue = aprs_queue
        self.running = True

    # Defines run sequence
    def run(self):
        while self.running:
            self.format_string(COMMENT)

    # Converts coordinates to APRS format string
    # For further explanation of APRS format, see http://www.aprs.org/doc/APRS101.PDF
    #   starting at page 32
    def format_string(self, comment):
        fix = self.aprs_queue.get()

        if fix:  # If value in queue is anything other than "None" Poison Pill
            # Time
            new_time = str(fix["time"])  # Time is in Zulu or UTC format
            time_day = new_time[8:10]
            time_hour = new_time[11:13]
            time_minute = new_time[14:16]
            # APRS Time format: ddhhmm
            # d = day of month, h = hour, m = minutes
            time_str = "{}{}{}".format(time_day, time_hour, time_minute)

            # Latitude
            latitude = fix["latitude"]  # Latitude provided is in decimal format
            lat_str = str(latitude)
            latitude_degrees = int(lat_str[0:2])  # Take the first two digits for degrees
            latitude_minutes = round(float(lat_str[2:]) * 60, 2)  # convert from decimal to minutes
            latmin_str = str(latitude_minutes).zfill(5)  # Minutes must be five digits
            # APRS Latitude Format: dd.mmmmm
            # d = degrees, m = minutes
            lat_str = str(latitude_degrees) + latmin_str

            # Longitude
            longitude = fix["longitude"]  # Longitude provided is in signed decimal format
            lon_str = str(longitude)
            lonbits = lon_str.split('.')
            longitude_degrees = abs(int(lonbits[0]))  # Take first two digits for degrees, make them unsigned
            lonmin = '.' + lonbits[1]
            longitude_minutes = round(float(lonmin) * 60, 2)  # convert from decimal to minutes
            londay_str = str(int(longitude_degrees)).zfill(3)  # Degrees must be three digits
            lonmin = "{0:.2f}".format(longitude_minutes)  # Seconds are separated by decimal
            lonmin_str = str(lonmin).zfill(5)  # Minutes must be five digits
            # APRS Longitude Format: dddmm.ss
            # d = degrees, m = minutes, s = seconds
            lon_str = londay_str + lonmin_str

            # Course
            course = round(fix["course"])  # Course rounded to nearest whole number
            course_str = str(course).zfill(3)  # Course must be three digits
            # APRS Course Format: ccc

            # Speed
            speed = round(fix["speed"] * 1.9438444924574)  # TODO: Get units for speed: Convert to knots or from knots?
            speed_str = str(speed).zfill(3)  # Speed must be three digits
            # APRS Speed format: sss

            # Altitude
            altitude = round(fix["altitude"] * 3.2808)  # read altitude, convert to feet
            alt_str = str(int(altitude)).zfill(6)
            # APRS Altitude format: aaaaaa

            aprs_string = '/{}z{}N/{}W>{}/{}{}/A={}'.format(time_str, lat_str, lon_str, course_str, speed_str,
                                                            comment, alt_str)

            # APRS formatted values, uncomment to view in terminal
            # print('Time: {}'.format(time_str))
            # print('Latitude: {}'.format(lat_str))
            # print('Longitude: {}'.format(lon_str))
            # print('Course: {}'.format(course_str))
            # print('Speed: {}'.format(speed_str))
            # print('Altitude: {}'.format(alt_str))

            self.aprs_queue.task_done()  # Mark position item in queue as done

            # Run Transmission code
            self.transmit(aprs_string)

        else:  # Poison pill detected
            self.running = False
            self.aprs_queue.task_done()

    # Make system call to encode APRS string to sound file, then plays through audio jack
    def transmit(self, transmit_string):
        print('Transmitting beacon.')
        print(transmit_string)
        call(['aprs', '-c', CALLSIGN, '-o', SOUNDFILE, transmit_string])  # creates packet.wav
        call(['aplay', SOUNDFILE])  # broadcasts packet.wav