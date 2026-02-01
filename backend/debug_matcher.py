import cv2
import numpy as np
import sys
import os

# Enable importing from current dir
sys.path.append(os.getcwd())

try:
    from app.utils.fingerprint_matcher import align_and_match_fingerprints
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def create_dummy_image():
    # Create a 200x200 image with random noise/lines
    img = np.zeros((200, 200), dtype=np.uint8)
    cv2.circle(img, (100, 100), 50, 255, 2)
    cv2.line(img, (0, 0), (200, 200), 255, 2)
    return img

try:
    print("Creating dummy images...")
    img1 = create_dummy_image()
    img2 = create_dummy_image()

    print("Running matcher...")
    result = align_and_match_fingerprints(img1, img2)
    print("Result keys:", result.keys())
    print("Score:", result["score"])
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
    print("FAILURE")
