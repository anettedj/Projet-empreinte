import os
import cv2
import glob
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import itertools
import random
from app.utils.manual_algo import manual_grayscale, manual_median_filter, manual_binarize, manual_thinning, extract_minutiae, manual_match

# Configuration
DATASET_DIR = "images/fvc/DB4_B"
OUTPUT_DIR = "metrics_output"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_person_id(filename):
    # FVC Format expected: 101_1.tif -> Person ID 101
    basename = os.path.basename(filename)
    name, ext = os.path.splitext(basename)
    parts = name.split('_')
    if len(parts) >= 1:
        return parts[0]
    return name

# Cache pour les minuties (pour ne pas re-traiter chaque image à chaque comparaison)
minutiae_cache = {}

def get_manual_minutiae(path):
    if path in minutiae_cache:
        return minutiae_cache[path]
    
    img = cv2.imread(path)
    if img is None: return None
    
    # Resize pour la vitesse (Indispensable pour le Zhang-Suen manuel en Python)
    img = cv2.resize(img, (150, 180)) 
    
    # Pipeline manuel
    gray = manual_grayscale(img)
    filtered = manual_median_filter(gray)
    binary = manual_binarize(filtered, invert=True)
    skeleton = manual_thinning(binary)
    m = extract_minutiae(skeleton)
    
    minutiae_cache[path] = m
    return m

def compute_metrics():
    print(f"Scanning dataset in {DATASET_DIR}...")
    files = glob.glob(os.path.join(DATASET_DIR, "*.tif"))
    
    if len(files) == 0:
        files = glob.glob(os.path.join(DATASET_DIR, "**", "*.tif"), recursive=True)

    if len(files) == 0:
        print(" Image non trouvée...")
        files = glob.glob(os.path.join(DATASET_DIR, "*.*"))
        files = [f for f in files if f.lower().endswith(('.tif', '.jpg', '.png', '.bmp'))]

    print(f" Found {len(files)} images.")

    files.sort()

    genuine_scores = []
    impostor_scores = []
    
    persons = {}
    for f in files:
        pid = get_person_id(f)
        if pid not in persons:
            persons[pid] = []
        persons[pid].append(f)

    print("Generating pairs...")
    
    genuine_pairs = []
    for pid, img_list in persons.items():
        pairs = list(itertools.combinations(img_list, 2))
        genuine_pairs.extend(pairs)

    impostor_pairs = []
    person_ids = list(persons.keys())
    target_impostor_count = 1000 # Un peu moins pour la vitesse
    
    while len(impostor_pairs) < target_impostor_count:
        id1, id2 = random.sample(person_ids, 2)
        img1 = random.choice(persons[id1])
        img2 = random.choice(persons[id2])
        impostor_pairs.append((img1, img2))

    print(f"Pairs generated: {len(genuine_pairs)} Genuine | {len(impostor_pairs)} Impostor")
    
    print("Running comparisons (MANUAL PIPELINE)...")
    
    # 1. Prétraiter toutes les images pour remplir le cache
    print("Preprocessing images...")
    for f in tqdm(files):
        get_manual_minutiae(f)

    # 2. Exécuter Authentiques
    print("--- Processing Genuine ---")
    for img1, img2 in tqdm(genuine_pairs):
        m1 = get_manual_minutiae(img1)
        m2 = get_manual_minutiae(img2)
        if m1 and m2:
            score, _ = manual_match(m1, m2)
            genuine_scores.append(score)

    # 3. Exécuter Imposteurs
    print("--- Processing Impostor ---")
    for img1, img2 in tqdm(impostor_pairs):
        m1 = get_manual_minutiae(img1)
        m2 = get_manual_minutiae(img2)
        if m1 and m2:
            score, _ = manual_match(m1, m2)
            impostor_scores.append(score)

    # Calcul des métriques
    thresholds = np.arange(0, 101, 1) # 0 to 100
    frr_list = []
    far_list = []
    
    genuine_scores = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)

    for t in thresholds:
        # FRR = Ratio des scores Authentiques SOUS le seuil
        # (Devraient être acceptés, mais ont été rejetés)
        fr_count = np.sum(genuine_scores < t)
        frr = (fr_count / len(genuine_scores)) * 100 if len(genuine_scores) > 0 else 0
        frr_list.append(frr)

        # FAR = Ratio des scores Imposteurs AU-DESSUS du seuil
        # (Devraient être rejetés, mais ont été acceptés)
        fa_count = np.sum(impostor_scores >= t)
        far = (fa_count / len(impostor_scores)) * 100 if len(impostor_scores) > 0 else 0
        far_list.append(far)

    # Trouver l'EER (Taux d'erreur égal) où le FAR croise le FRR
    # Utiliser la différence min simple
    diffs = np.abs(np.array(frr_list) - np.array(far_list))
    eer_idx = np.argmin(diffs)
    eer_threshold = thresholds[eer_idx]
    eer_value = (frr_list[eer_idx] + far_list[eer_idx]) / 2

    print(f"\n ANALYSIS COMPLETE")
    print(f"Genuine Scores: Avg={np.mean(genuine_scores):.2f}, Max={np.max(genuine_scores):.2f}, Min={np.min(genuine_scores):.2f}")
    print(f"Impostor Scores: Avg={np.mean(impostor_scores):.2f}, Max={np.max(impostor_scores):.2f}, Min={np.min(impostor_scores):.2f}")
    print(f"Optimal Threshold (EER Point): {eer_threshold}")
    print(f"EER Value (approx error rate): {eer_value:.2f}%")
    print(f"At this threshold: FRR={frr_list[eer_idx]:.2f}%, FAR={far_list[eer_idx]:.2f}%")

    # Tracé FRR/FAR vs Seuil
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, frr_list, label='Taux de Faux Rejet (FRR)', color='red', linewidth=2)
    plt.plot(thresholds, far_list, label='Taux de Fausse Acceptation (FAR)', color='blue', linewidth=2)
    plt.axvline(x=eer_threshold, color='green', linestyle='--', label=f'Optimal Threshold ({eer_threshold})')
    plt.xlabel('Threshold (Score 0-100)')
    plt.ylabel('Taux d erreur (%)')
    plt.title('Performance Metrics: FRR vs FAR')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'frr_far_curves.png'))
    print(f"Graph saved to {OUTPUT_DIR}/frr_far_curves.png")

    # Tracé Courbe ROC
    # ROC est typiquement GAR (Taux d'Acceptation Authentique = 1 - FRR) vs FAR
    gar_list = [100 - x for x in frr_list]
    
    plt.figure(figsize=(10, 6))
    plt.plot(far_list, gar_list, color='purple', linewidth=2)
    plt.plot([0, 100], [0, 100], color='gray', linestyle='--') 
    plt.xlabel('False Acceptance Rate (FAR) %')
    plt.ylabel('Genuine Acceptance Rate (GAR) %')
    plt.title('ROC Curve')
    plt.xlim([0, 20]) 
    plt.ylim([80, 100])
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, 'roc_curve.png'))
    print(f"ROC Graph saved to {OUTPUT_DIR}/roc_curve.png")

if __name__ == "__main__":
    try:
        compute_metrics()
    except ImportError as e:
        print("Missing required libraries. Installing them...")
        os.system("pip install matplotlib tqdm")
        print("Please rerun the script.")
    except Exception as e:
        print(f"An error occurred: {e}")
