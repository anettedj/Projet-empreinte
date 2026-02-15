
import cv2
import numpy as np
import os

def compare_images(p1, p2):
    img1 = cv2.imread(p1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(p2, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        return "One image could not be loaded"
    if img1.shape != img2.shape:
        return f"Shapes differ: {img1.shape} vs {img2.shape}"
    diff = cv2.absdiff(img1, img2)
    non_zero = np.count_nonzero(diff)
    if non_zero == 0:
        return "Exactly identical pixels"
    else:
        return f"Different pixels: {non_zero} out of {img1.size}"

path1 = "images/fvc/DB1_B/101_1.tif"
path2 = "images/fvc/DB1_B (1)/101_1.tif"

print(f"Comparing {path1} and {path2}:")
print(compare_images(path1, path2))

path3 = "images/fvc/DB3_B/105_1.tif"
path4 = "images/fvc/DB3_B (1)/105_1.tif"
path5 = "images/fvc/DB3_Bj/105_1.tif"

if os.path.exists(path3) and os.path.exists(path4):
    print(f"\nComparing {path3} and {path4}:")
    print(compare_images(path3, path4))

if os.path.exists(path4) and os.path.exists(path5):
    print(f"\nComparing {path4} and {path5}:")
    print(compare_images(path4, path5))
