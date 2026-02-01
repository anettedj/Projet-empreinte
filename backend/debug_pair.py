import cv2
import os
from app.utils.fingerprint_matcher import align_and_match_fingerprints

# Hardcoded paths based on known structure
img1_path = "images/fvc/DB4_B/101_1.tif"
img2_path = "images/fvc/DB4_B/101_2.tif"

print(f"DEBUG: Testing match between {img1_path} and {img2_path}")
print(f"DEBUG: CWD is {os.getcwd()}")
print(f"DEBUG: img1 exists? {os.path.exists(img1_path)}")

try:
    if os.path.exists(img1_path):
        img = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
        print(f"DEBUG: img1 load shape: {img.shape if img is not None else 'None'}")

    result = align_and_match_fingerprints(img1_path, img2_path)
    print("DEBUG: Result Result:", result)
except Exception as e:
    print(f"DEBUG: Error occurred: {e}")
