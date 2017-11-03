# gps_aprs.py
#
# This script runs indefinitely, pulling the GPS coordinates from the local gps daemon server
# It then converts the data to APRS format, creates an APRS soundfile and broadcasts
#
# This script is adapted from Super Simple APRS Position Reporter by Midnight Cheese
# http://midnightcheese.com/2015/12/super-simple-aprs-position-beacon/
#
# This script assumes there is a gpsd daemon running. Before running this script, enter
#    sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
# in the console


import json, requests
import time
from subprocess import call

# TODO: Extract these variables to config file
GPS_SLEEPTIME = 5

# Global variables for this module only
CALLSIGN = "KC1HZL-7"
COMMENT = "Testing RaspPi + UV-5R"
SOUNDFILE = "packet.wav"


while 1:
    url = requests.get("http://localhost/gpsd.php?op=json")  # get text from gpsd server
    data = json.loads(url.text)
    try:
        # Time
        now_time = data['tpv'][0]['time']  # read time from JSON
        timeday = now_time[8:10]
        timehour = now_time[11:13]
        timeminute = now_time[14:16]
        time_str = timeday + timehour + timeminute  # make APRS-compatible string
        print('Time: {}'.format(time_str))

        # Latitude
        lat = str(data['tpv'][0]['lat'])  # read latitude from JSON
        latday = lat[0:2]
        latmin = round(float(lat[2:]) * 60, 2)  # convert from decimal to minutes
        latmin = "{0:.2f}".format(latmin)
        latmin_str = str(latmin).zfill(5)
        lat_string = latday + latmin_str  # make APRS-compatible string
        print('Latitude: {}'.format(lat_string))

        # Longitude
        lon = str(data['tpv'][0]['lon'])  # read longitude from JSON
        lonbits = lon.split('.')
        londay = lonbits[0]
        londay_str = str(int(londay)).zfill(3)
        lonmin = '.' + lonbits[1]
        lonmin = round(float(lonmin) * 60, 2)  # convert from decimal to minutes
        lonmin = "{0:.2f}".format(lonmin)
        lonmin_str = str(lonmin).zfill(5)
        lon_string = londay_str + lonmin_str  # make APRS-compatible string
        print('Longitude: {}'.format(lon_string))

        course = round(data['tpv'][0]['track'])  # read course from JSON
        course_str = str(course).zfill(3)  # make APRS-compatible string
        print('Track: {}'.format(course_str))

        speed = data['tpv'][0]['speed'] * 1.9438444924574   # read speed from JSON
        speed = round(speed)
        speed_str = str(speed).zfill(3)  # make APRS-compatible string
        print('Speed: {}'.format(speed_str))

        alt = round(data['tpv'][0]['alt'] * 3.2808)  # read altitude from JSON, convert to meters
        alt_str = str(alt).zfill(6)  # make APRS-compatible string
        print('Altitude: {}'.format(alt_str))

        create_audio_command = '"/' + time_str + 'z' + lat_string + 'N/' + lon_string + 'W>' + \
                               course_str + '/' + speed_str + COMMENT + '/A=' + alt_str + '"'  # build APRS string
    except KeyError:  # cannot get data from gpsd server
        print('No GPS data is available.')
    else:
        print('Transmitting beacon.')
        call(['aprs', '-c', CALLSIGN, '-o', SOUNDFILE, create_audio_command])  # creates packet.wav
        time.sleep(2)
        call(['aplay', SOUNDFILE])  # broadcasts packet.wav
    time.sleep(GPS_SLEEPTIME)
