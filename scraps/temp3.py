import cv2
import numpy as np
from glob import glob
from PIL import Image
from pprint import pprint
from os.path import join

fs = glob("C:\\Users\\bruno\\OneDrive\\Pictures\\button*.png")

for f in fs:
    img = cv2.imread(f)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    alpha = 0.3
    img = img.astype(float)
    for i, v in enumerate((0, 255, 0)):
        img[:, :, i] = img[:, :, i] * (1 - alpha) + v * alpha
    img = np.clip(img, 0, 255).astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    fname = f.split("/")[-1].replace(".png", "")
    cv2.imwrite(join("C:\\Users\\bruno\\OneDrive\\Pictures\\", fname + "_green.png"), img)
    # Image.fromarray(img).show()
    # exit()