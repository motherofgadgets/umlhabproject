from subprocess import call
import threading

CALLSIGN = "KC1HZL-7"
COMMENT = "Testing RaspPi + UV-5R"
SOUNDFILE = "packet.wav"


class Aprs(threading.Thread):
    def __init__(self, aprs_queue):
        threading.Thread.__init__(self)
        self.aprs_queue = aprs_queue
        self.running = True

    def run(self):
        while self.running:
            self.format_string(COMMENT)

    def format_string(self, comment):
        fix = self.aprs_queue.get()

        if fix:
            # Time
            new_time = str(fix["time"])
            time_day = new_time[8:10]
            time_hour = new_time[11:13]
            time_minute = new_time[14:16]
            time_str = "{}{}{}".format(time_day, time_hour, time_minute)

            # Latitude
            latitude = fix["latitude"]
            lat_str = str(latitude)
            latitude_degrees = int(lat_str[0:2])
            latitude_minutes = round(float(lat_str[2:]) * 60, 2)  # convert from decimal to minutes
            latmin_str = str(latitude_minutes).zfill(5)
            lat_str = str(latitude_degrees) + latmin_str

            # Longitude
            longitude = fix["longitude"]
            lon_str = str(longitude)
            lonbits = lon_str.split('.')
            longitude_degrees = abs(int(lonbits[0]))
            lonmin = '.' + lonbits[1]
            longitude_minutes = round(float(lonmin) * 60, 2)  # convert from decimal to minutes
            londay_str = str(int(longitude_degrees)).zfill(3)
            lonmin = "{0:.2f}".format(longitude_minutes)
            lonmin_str = str(lonmin).zfill(5)
            lon_str = londay_str + lonmin_str

            # Course
            course = round(fix["course"])
            course_str = str(course).zfill(3)

            # Speed
            speed = round(fix["speed"] * 1.9438444924574)
            speed_str = str(speed).zfill(3)

            # Altitude
            altitude = round(fix["altitude"] * 3.2808)  # read altitude, convert to meters
            alt_str = str(int(altitude)).zfill(6)

            aprs_string = '/{}z{}N/{}W>{}/{}{}/A={}'.format(time_str, lat_str, lon_str, course_str, speed_str,
                                                            comment, alt_str)
            #
            # print('TimeDay: {}'.format(time_day))
            # print('TimeHour: {}'.format(time_hour))
            # print('TimeMinute: {}'.format(time_minute))

            # print('Time: {}'.format(time_str))
            # print('Latitude: {}'.format(lat_str))
            # print('Longitude: {}'.format(lon_str))
            # print('Course: {}'.format(course_str))
            # print('Speed: {}'.format(speed_str))
            # print('Altitude: {}'.format(alt_str))

            self.aprs_queue.task_done()

            self.transmit(aprs_string)
        else:
            self.running = False
            print('APRS running = False')
            self.aprs_queue.task_done()

    def transmit(self, transmit_string):
        print('Transmitting beacon.')
        print(transmit_string)
        call(['aprs', '-c', CALLSIGN, '-o', SOUNDFILE, transmit_string])  # creates packet.wav
        call(['aplay', SOUNDFILE])  # broadcasts packet.wav