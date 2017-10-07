# importing csv, senseHAT and time packages 
import csv
import numpy as np
from sense_hat import SenseHat
import time
from datetime import datetime

def get_sense_data():
    sense_data=[]
    sense_data.append(datetime.now())
    sense_data.append(sense.get_temperature_from_humidity())
    sense_data.append(sense.get_temperature_from_pressure())
    sense_data.append(sense.get_humidity())
    sense_data.append(sense.get_pressure())
    o = sense.get_orientation()
    yaw = o["yaw"]
    pitch = o["pitch"]
    roll = o["roll"]
    sense_data.extend([pitch,roll,yaw])

    mag = sense.get_compass_raw()
    mag_x = mag["x"]
    mag_y = mag["y"]
    mag_z = mag["z"]
    sense_data.extend([mag_x,mag_y,mag_z])

    acc = sense.get_accelerometer_raw()
    x = acc["x"]
    y = acc["y"]
    z = acc["z"]
    sense_data.extend([x,y,z])

    gyro = sense.get_gyroscope_raw()
    gyro_x = gyro["x"]
    gyro_y = gyro["y"]
    gyro_z = gyro["z"]
    sense_data.extend([gyro_x,gyro_y,gyro_z])
    
    return sense_data

def log_data():
  output_string = ",".join(str(value) for value in sense_data)
  batch_data.append(output_string)

def file_setup(filename):
  header  =["timestamp","temp_h","temp_p","humidity","pressure","orient","compass","accn","gyro"]

  with open(filename,"w") as f:
      f.write(",".join(str(value) for value in header)+ "\n")


# Getting and storing Data
FILENAME = "testLog"
WRITE_FREQUENCY = 5

sense = SenseHat()
sense.clear()

batch_data= []

if FILENAME =="":
    filename = "testLog.csv"
else:
    filename = FILENAME+".csv"

file_setup(filename)





while True:
    time.sleep(1)
    sense_data = get_sense_data()
    log_data()

    if len(batch_data) >= WRITE_FREQUENCY:
        print("Writing to file..")
        with open(filename, "a") as f:
            for line in batch_data:
                f.write(line + "\n")
            batch_data = []
    print(sense_data)


