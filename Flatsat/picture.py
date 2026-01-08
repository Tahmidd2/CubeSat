"""
The Python code you will write for this module should read
acceleration data from the IMU. When a reading comes in that surpasses
an acceleration threshold (indicating a shake), your Pi should pause,
trigger the camera to take a picture, then save the image with a
descriptive filename. You may use GitHub to upload your images automatically,
but for this activity it is not required.

The provided functions are only for reference, you do not need to use them. 
You will need to complete the take_photo() function and configure the VARIABLES section
"""

# AUTHOR: Tahmid Islam
# DATE: 1/7/26

import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2

# vars
THRESHOLD = 15.0    # acceleration threshold, not sure if this is right
REPO_PATH = "/home/pi/CubeSat" # depends on what david stored locally
FOLDER_PATH = "/Images" 
NAME = "TahmidI" # 

# hardware
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)  # 6-DoF IMU (accelerometer + gyro)
mag = LIS3MDL(i2c)         # 3-axis magnetometer
picam2 = Picamera2()       # pi Camera
picam2.start_preview()
time.sleep(2)

# functions

def git_push():
    """
    Stages, commits, and pushes new images to your GitHub repo.
    """
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()  # pull
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        origin.push()
        print('Pushed new photo to GitHub.')
    except Exception as e:
        print("Couldn't upload to git:", e)


def img_gen(name):
    """
    Generates a descriptive image filename based on the current time.

    Parameters:
        name (str): Your name, ex. MasonM
    """
    t = time.strftime("_%H%M%S")
    imgname = f'{REPO_PATH}{FOLDER_PATH}/{name}{t}.jpg'
    return imgname


def take_photo():
    """
    Continuously monitors accelerometer data. When a shake above the threshold
    is detected, takes a photo and saves it to the GitHub repo folder.
    """
    print("Checking for shakes")
    while True:
        # getting the value
        accelx, accely, accelz = accel_gyro.acceleration # this should be in m/s^2?

        # is this right?
        total_accel = (accelx**2 + accely**2 + accelz**2)**0.5

        # conditional
        if total_accel > THRESHOLD:
            print(f"Shake detected! Acceleration: {total_accel:.2f} m/s^2")
            
            # creates file
            filename = img_gen(NAME)
            print(f"Taking photo: {filename}")
            
            # takes image
            picam2.capture_file(filename)
            print("Photo taken.")

            # pushes
            git_push()

            # delay for hardware
            time.sleep(5)

        # delay
        time.sleep(0.1)


def main():
    take_photo()


if __name__ == '__main__':
    main()