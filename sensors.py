# importing csv, senseHAT and time packages
import csv
import numpy as np
from sense_hat import SenseHat
import time
from datetime import datetime
import threading
import os
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
FILEPATH = 'sensor_logs/'
FILENAME = time.strftime('%Y-%m-%d_%H%M%S')
WRITE_FREQUENCY = Config.getfloat('TimingIntervals', 'SensorLogging')


class Sensors(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.sense = SenseHat()
        self.sense.clear()

        self.batch_data = []

        if not os.path.exists(FILEPATH):
            os.makedirs(FILEPATH)

        if FILENAME == "":
            self.filename = "{}testLog.csv".format(FILEPATH)
        else:
            self.filename = '{}{}.csv'.format(FILEPATH, FILENAME)

        self.file_setup(self.filename)
        self.running = True

    def run(self):
        while self.running:
            time.sleep(1)
            sense_data = self.get_sense_data()
            self.log_data(sense_data)

            if len(self.batch_data) >= WRITE_FREQUENCY:
                print("Writing to file..")
                with open(self.filename, "a") as f:
                    for line in self.batch_data:
                        f.write(line + "\n")
                    self.batch_data = []
            print(sense_data)

    def get_sense_data(self):
        sense_data = []
        sense_data.append(datetime.now())
        sense_data.append(self.sense.get_temperature_from_humidity())
        sense_data.append(self.sense.get_temperature_from_pressure())
        sense_data.append(self.sense.get_humidity())
        sense_data.append(self.sense.get_pressure())
        o = self.sense.get_orientation()
        yaw = o["yaw"]
        pitch = o["pitch"]
        roll = o["roll"]
        sense_data.extend([pitch, roll, yaw])

        mag = self.sense.get_compass_raw()
        mag_x = mag["x"]
        mag_y = mag["y"]
        mag_z = mag["z"]
        sense_data.extend([mag_x, mag_y, mag_z])

        acc = self.sense.get_accelerometer_raw()
        x = acc["x"]
        y = acc["y"]
        z = acc["z"]
        sense_data.extend([x, y, z])

        gyro = self.sense.get_gyroscope_raw()
        gyro_x = gyro["x"]
        gyro_y = gyro["y"]
        gyro_z = gyro["z"]
        sense_data.extend([gyro_x, gyro_y, gyro_z])

        return sense_data


    def log_data(self, sense_data):
        output_string = ",".join(str(value) for value in sense_data)
        self.batch_data.append(output_string)


    def file_setup(self, filename):
        header = ["timestamp", "temp_h", "temp_p", "humidity", "pressure", "orient", "compass", "accn", "gyro"]

        with open(filename, "w") as f:
            f.write(",".join(str(value) for value in header) + "\n")




