"""
Reads acceleration data from the IMU. When a shake above a threshold
is detected, the Raspberry Pi pauses, takes a photo, and saves it
with a descriptive filename.
"""

# AUTHOR: Tahmid Islam
# DATE: 1/7/26

import time
import board
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2
import math
import os

# config

THRESHOLD = 3.0  # Shake threshold (m/s^2 above gravity)
COOLDOWN = 5     # Seconds between photos
REPO_PATH = "home/palace-stuy/GITHUB/Cubesat/Flatsat"
FOLDER_PATH = "/Images"
NAME = "TahmidI"

# hardware

i2c = board.I2C()

# imu
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

# cam
picam2 = Picamera2()
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()
time.sleep(2)

# folder check
os.makedirs(REPO_PATH + FOLDER_PATH, exist_ok=True)

# funcitons

def git_push():
    """
    Stages, commits, and pushes new images to GitHub.
    (Optional – comment out when testing offline)
    """
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        origin.pull()
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        origin.push()
        print("GitHub upload complete.")
    except Exception as e:
        print("Git upload failed:", e)


def img_gen(name):
    """
    Generates a timestamped image filename.
    """
    t = time.strftime("_%H%M%S")
    return f"{REPO_PATH}{FOLDER_PATH}/{name}{t}.jpg"


def take_photo():
    """
    Monitors acceleration. When a shake is detected,
    captures and saves a photo.
    """
    print("FlatSat active — waiting for shake...")
    last_photo_time = 0

    while True:

        ax, ay, az = accel_gyro.acceleration

        total_accel = math.sqrt(ax**2 + ay**2 + az**2)

        shake = abs(total_accel - 9.8)

        current_time = time.time()

        if shake > THRESHOLD and (current_time - last_photo_time) > COOLDOWN:
            print(f"Shake detected! Δa = {shake:.2f} m/s^2")

            filename = img_gen(NAME)
            print(f"Taking photo: {filename}")

            try:
                picam2.capture_file(filename)
                print("Photo saved.")
                git_push()
            except Exception as e:
                print("Camera error:", e)

            last_photo_time = current_time

        time.sleep(0.1)

# main

def main():
    take_photo()


if __name__ == "__main__":
    main()
