import csv
import numpy as np
import pickle

with open("dist.csv", 'r') as f:
    reader = csv.reader(f)
    dist = np.array(list(reader)).astype('float')

with open("mtx.csv", 'r') as f:
    reader = csv.reader(f)
    cameraMatrix = np.array(list(reader)).astype('float')

calibrationData = {
    "cameraMatrix": cameraMatrix,
    "dist": dist,
}
with open("calibration.pkl", "wb") as f:
    print(calibrationData)
    pickle.dump(calibrationData, f)
    print(f"Calibration data saved to calibration.pkl")
