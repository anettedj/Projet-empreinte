import cv2
import numpy as np
from app.utils.manual_algo import manual_grayscale, manual_median_filter, manual_binarize, manual_thinning, extract_minutiae, manual_match

def test_manual_pipeline():
    img1_path = "images/fvc/DB4_B/101_1.tif"
    img2_path = "images/fvc/DB4_B/101_2.tif"
    
    print(f"--- Testing Manual Pipeline ---")
    
    def process_file(path, name):
        print(f"Processing {path}...")
        img = cv2.imread(path)
        if img is None:
            print("Error: Image not found")
            return None
            
        # Resize to speed up manual processing
        img = cv2.resize(img, (200, 240)) # Half size approx
        
        # 1. Grayscale
        gray = manual_grayscale(img)
        cv2.imwrite(f"debug_{name}_1_gray.jpg", gray)
        
        # 2. Median Filter
        filtered = manual_median_filter(gray)
        cv2.imwrite(f"debug_{name}_2_filtered.jpg", filtered)
        
        # 3. Binarize (Inverted for dark ridges)
        binary = manual_binarize(filtered, invert=True)
        cv2.imwrite(f"debug_{name}_3_binary.jpg", binary)
        
        # 4. Thinning
        skeleton = manual_thinning(binary)
        cv2.imwrite(f"debug_{name}_4_skeleton.jpg", skeleton)
        
        # 5. Extraction
        minutiae = extract_minutiae(skeleton)
        
        return minutiae, skeleton

    m1, s1 = process_file(img1_path, "img1")
    m2, s2 = process_file(img2_path, "img2")
    
    print(f"Minutiae Image 1: {len(m1[0])} Terms, {len(m1[1])} Bifs")
    print(f"Minutiae Image 2: {len(m2[0])} Terms, {len(m2[1])} Bifs")
    
    # Matching
    score, matches = manual_match(m1, m2)
    print(f"Result: {matches} matches found. Score: {score}%")

if __name__ == "__main__":
    test_manual_pipeline()
