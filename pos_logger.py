# pos_logger.py
#
# by Danae Moss
#
# This script runs indefinitely, receiving GPS coordinates through a queue from the position script.
# It then puts that data in an array with each value separated by commas. That array is then written
# to a log file.
#
# Logging pattern adapted from original sensehat3.py by Ruchit Panchal
#

import ConfigParser
from gps import *  # Using GPSD library from http://catb.org/gpsd/
import threading
import os

# Obtains user-defined logging frequency parameter through config file
Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
FILEPATH = 'position_logs/'
FILENAME = time.strftime('%Y-%m-%d_%H%M%S')
LOG_FREQUENCY = Config.getfloat('TimingIntervals', 'PositionLogging')


class PosLogger(threading.Thread):
    # Initiates an instance of itself as a thread, sets to running
    def __init__(self, log_queue):
        threading.Thread.__init__(self)
        self.log_queue = log_queue
        self.batch_data = []

        # If the directory does not exist, create it
        if not os.path.exists(FILEPATH):
            os.makedirs(FILEPATH)

        # If no filename specified, use default
        if FILENAME == "":
            self.filename = "{}testLog.csv".format(FILEPATH)
        else:
            self.filename = '{}{}.csv'.format(FILEPATH, FILENAME)

        file_setup(self.filename)
        self.running = True

    # Defines run sequence
    def run(self):
        while self.running:
            self.log_data()
            # Check if there are enough items in batch_data to write to log
            if len(self.batch_data) >= LOG_FREQUENCY:
                print("Writing to file..")
                with open(self.filename, "a") as f:
                    for line in self.batch_data:
                        f.write(line + "\n")
                    self.batch_data = []

    # Puts position data into array of strings, joins with comma separator for csv and pushes to batch
    def log_data(self):  # If value in queue is anything other than "None" Poison Pill
        log_fix = self.log_queue.get()
        if log_fix:
            if isinstance(log_fix["time"], float):  # Occasionally, time will change format to float.
                log_time = time.strftime('%Y-%m-%dT%H:%M:%S.%000Z', time.gmtime(log_fix["time"]))  # Converts to utc
            else:
                log_time = log_fix["time"]
            # Places each position element in single array
            pos_data = [log_time,
                        log_fix["latitude"],
                        log_fix["longitude"],
                        log_fix["course"],
                        log_fix["speed"],
                        log_fix["altitude"]]
            # Joins all position elements into csv string with comma delimiter
            output_string = ",".join(str(value) for value in pos_data)
            self.batch_data.append(output_string)
            self.log_queue.task_done()  # Mark position item in queue as done
        else:  # Poison pill detected
            self.running = False
            self.log_queue.task_done()  # Mark position item in queue as done


# Sets up header row for csv file
def file_setup(filename):
    header = ["timestamp", "Latitude", "Longitude", "Course", "Speed", "Altitude"]

    with open(filename, "w") as f:
        f.write(",".join(str(value) for value in header) + "\n")