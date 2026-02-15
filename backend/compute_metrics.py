import os
import cv2
import glob
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import itertools
import random
import json
from matplotlib.ticker import MultipleLocator
from datetime import datetime
from app.utils.manual_algo import complete_preprocessing_pipeline, manual_match

# Configuration
DATASET_ROOT = "images/fvc"
OUTPUT_DIR = "metrics_output"
CONFIG_DIR = "config"
DATASET_DIRS = [
    "DB1_B", "DB3_B", "DB4_B", 
    "DB1_B(1)", "DB2_B(1)", "DB3_B(1)", "DB4_B(1)", "DB3_Bj"
]

for d in [OUTPUT_DIR, CONFIG_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

def get_person_id(filename):
    name = os.path.splitext(os.path.basename(filename))[0]
    return name.split('_')[0]

# Cache pour les minuties
MINUTIAE_CACHE_FILE = os.path.join(CONFIG_DIR, "minutiae_cache.json")
minutiae_cache = {}

if os.path.exists(MINUTIAE_CACHE_FILE):
    try:
        with open(MINUTIAE_CACHE_FILE, "r") as f:
            # Convert keys back to string (paths) and values to tuples
            minutiae_cache = json.load(f)
    except:
        minutiae_cache = {}

def save_minutiae_cache():
    with open(MINUTIAE_CACHE_FILE, "w") as f:
        json.dump(minutiae_cache, f)

def get_manual_minutiae(path):
    if path in minutiae_cache:
        # JSON convertit les listes, on doit les transformer en tuples pour manual_match si besoin
        # Mais manual_match accepte des listes, donc on garde tel quel
        return minutiae_cache[path]
    
    img = cv2.imread(path)
    if img is None: return None
    
    # Utiliser le pipeline complet
    m, s = complete_preprocessing_pipeline(img)
    
    # Stocker sous forme de listes pour JSON
    minutiae_cache[path] = [m[0], m[1]]
    return minutiae_cache[path]

def compute_metrics():
    print(f"====================================================")
    print(f"📊 CALCUL DES MÉTRIQUES BIOMÉTRIQUES (FAR/FRR)")
    print(f"====================================================")
    
    print(f"🔍 Scan des bases de données...")
    files = []
    for d in DATASET_DIRS:
        d_path = os.path.join(DATASET_ROOT, d)
        if os.path.exists(d_path):
            found = glob.glob(os.path.join(d_path, "*.tif"))
            print(f"  • {d}: {len(found)} images")
            files.extend(found)
    
    if len(files) == 0:
        print("❌ Aucune image .tif trouvée.")
        return

    print(f"\n✅ Total images: {len(files)}")
    files.sort()

    # Grouper par dataset + personne
    persons = {}
    for f in files:
        pid = get_person_id(f)
        db = os.path.basename(os.path.dirname(f))
        key = f"{db}_{pid}"
        if key not in persons:
            persons[key] = []
        persons[key].append(f)

    # Générer les paires
    genuine_pairs = []
    for key, img_list in persons.items():
        pairs = list(itertools.combinations(img_list, 2))
        genuine_pairs.extend(pairs)

    impostor_pairs = []
    person_keys = list(persons.keys())
    # On limite pour la vitesse mais on garde une validité statistique
    target_impostor_count = min(2000, len(files) * 2) 
    
    while len(impostor_pairs) < target_impostor_count:
        k1, k2 = random.sample(person_keys, 2)
        if k1 == k2: continue
        img1 = random.choice(persons[k1])
        img2 = random.choice(persons[k2])
        impostor_pairs.append((img1, img2))

    print(f"📈 Paires générées: {len(genuine_pairs)} Authentiques | {len(impostor_pairs)} Imposteurs")
    
    # Prétraitement
    print("\n⚙️  Prétraitement des images (Pipeline 10 étapes)...")
    try:
        count = 0
        for f in tqdm(files):
            get_manual_minutiae(f)
            count += 1
            if count % 50 == 0:
                save_minutiae_cache()
    finally:
        save_minutiae_cache()
        print("\n💾 Cache des minuties sauvegardé (intermédiaire/final).")

    # Comparaisons (avec cache disque et log détaillé)
    cache_file = os.path.join(CONFIG_DIR, "scores_cache.json")
    log_file = os.path.join(OUTPUT_DIR, "detailed_comparisons.csv")
    
    import csv
    
    if os.path.exists(cache_file):
        print("\n📂 Chargement des scores depuis le cache...")
        with open(cache_file, "r") as f:
            data = json.load(f)
            genuine_scores = data["genuine"]
            impostor_scores = data["impostor"]
    else:
        genuine_scores = []
        impostor_scores = []
        
        with open(log_file, mode='w', newline='', encoding='utf-8') as csvfile:
            log_writer = csv.writer(csvfile)
            log_writer.writerow(['Type', 'Database', 'Image 1', 'Image 2', 'Matches', 'Total Minutiae', 'Score (%)'])
            
            print("\n🔄 Exécution des comparaisons (Authentiques)...")
            for img1, img2 in tqdm(genuine_pairs, desc="Authentiques"):
                m1 = get_manual_minutiae(img1)
                m2 = get_manual_minutiae(img2)
                if m1 and m2:
                    score, matches = manual_match(m1, m2)
                    genuine_scores.append(score)
                    total_min = (len(m1[0])+len(m1[1])) + (len(m2[0])+len(m2[1]))
                    db_name = os.path.basename(os.path.dirname(img1))
                    log_writer.writerow(['Genuine', db_name, os.path.basename(img1), os.path.basename(img2), matches, total_min, score])

            print("\n🔄 Exécution des comparaisons (Imposteurs)...")
            for img1, img2 in tqdm(impostor_pairs, desc="Imposteurs"):
                m1 = get_manual_minutiae(img1)
                m2 = get_manual_minutiae(img2)
                if m1 and m2:
                    score, matches = manual_match(m1, m2)
                    impostor_scores.append(score)
                    total_min = (len(m1[0])+len(m1[1])) + (len(m2[0])+len(m2[1]))
                    db_name = os.path.basename(os.path.dirname(img1))
                    log_writer.writerow(['Impostor', db_name, os.path.basename(img1), os.path.basename(img2), matches, total_min, score])
        
        # Sauvegarder scores pour re-plotting rapide
        with open(cache_file, "w") as f:
            json.dump({"genuine": genuine_scores, "impostor": impostor_scores}, f)
        print(f"✅ Log détaillé sauvegardé dans {log_file}")

    # Statistiques
    genuine_scores = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)
    
    thresholds = np.arange(0, 101, 1)
    frr_list = []
    far_list = []

    for t in thresholds:
        frr = (np.sum(genuine_scores < t) / len(genuine_scores)) * 100
        far = (np.sum(impostor_scores >= t) / len(impostor_scores)) * 100
        frr_list.append(frr)
        far_list.append(far)

    # EER
    diffs = np.abs(np.array(frr_list) - np.array(far_list))
    eer_idx = np.argmin(diffs)
    eer_threshold = thresholds[eer_idx]
    eer_value = (frr_list[eer_idx] + far_list[eer_idx]) / 2

    print(f"\n====================================================")
    print(f"🎯 RÉSULTATS DE L'ANALYSE")
    print(f"====================================================")
    print(f"• Score Authentique Moyen: {np.mean(genuine_scores):.2f}%")
    print(f"• Score Imposteur Moyen:   {np.mean(impostor_scores):.2f}%")
    print(f"• SEUIL OPTIMAL (EER):    {eer_threshold}%")
    print(f"• VALEUR EER:             {eer_value:.2f}%")
    print(f"====================================================")

    # Sauvegarde config
    optimal_config = {
        "threshold": float(eer_threshold),
        "eer": float(eer_value),
        "avg_genuine": float(np.mean(genuine_scores)),
        "avg_impostor": float(np.mean(impostor_scores)),
        "date": datetime.now().isoformat(),
        "raw_data": {
            "thresholds": thresholds.tolist(),
            "frr": frr_list,
            "far": far_list
        }
    }
    with open(os.path.join(CONFIG_DIR, "optimal_threshold.json"), "w") as f:
        json.dump(optimal_config, f, indent=2)

    # Graphs
    plt.figure(figsize=(24, 10)) # Plus large pour accommoder toutes les graduations
    plt.plot(thresholds, frr_list, label='FRR (Faux Rejet)', color='red', linewidth=2)
    plt.plot(thresholds, far_list, label='FAR (Fausse Acceptation)', color='blue', linewidth=2)
    
    # Seuil EER
    plt.axvline(x=eer_threshold, color='green', linestyle='--', alpha=0.7)
    plt.text(eer_threshold+0.5, eer_value+2, f'EER: {eer_threshold}%', color='green', weight='bold')

    # Graduations à pas de 1
    ax = plt.gca()

    ax.xaxis.set_major_locator(MultipleLocator(1))   # Force pas = 1
    ax.set_xticks(np.arange(0, 101, 1))              # Imposer toutes les positions
    ax.tick_params(axis='x', labelrotation=90, labelsize=8)

    plt.yticks(np.arange(0, 101, 5))

    
    plt.xlabel('Seuil de Score (%) - Pas de 1', fontsize=12, labelpad=10)
    plt.ylabel('Taux d erreur (%)', fontsize=12)
    plt.title('Courbes FAR / FRR - Graduation Détaillée (Pas = 1)', fontsize=14, weight='bold')
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'far_frr_curves.png'), dpi=150)
    print(f"\n✅ Graphique détaillé sauvegardé dans {OUTPUT_DIR}")

if __name__ == "__main__":
    compute_metrics()
