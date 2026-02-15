import cv2
import numpy as np
import os
from app.utils.manual_algo import complete_preprocessing_pipeline, manual_match

def test_manual_pipeline():
    # Chemins des images pour le test
    img1_path = "images/fvc/DB4_B/101_1.tif"
    img2_path = "images/fvc/DB4_B/101_2.tif" # Même personne
    img3_path = "images/fvc/DB4_B/102_1.tif" # Personne différente
    
    # Vérifier l'existence des fichiers
    for p in [img1_path, img2_path, img3_path]:
        if not os.path.exists(p):
            print(f"❌ Erreur: Image non trouvée à {p}")
            return

    print(f"--- 🧪 TEST DU PIPELINE BIOMÉTRIQUE COMPLET ---")
    
    def run_case(p1, p2, label):
        print(f"\n--- Cas: {label} ---")
        img1 = cv2.imread(p1)
        img2 = cv2.imread(p2)
        
        print(f"  Traitement Image A...")
        m1, s1 = complete_preprocessing_pipeline(img1)
        print(f"    Minuties extraites: {len(m1[0])+len(m1[1])}")
        
        print(f"  Traitement Image B...")
        m2, s2 = complete_preprocessing_pipeline(img2)
        print(f"    Minuties extraites: {len(m2[0])+len(m2[1])}")
        
        # Matching
        score, matches = manual_match(m1, m2)
        print(f"  🎯 RESULTAT: {matches} correspondances. SCORE BIOMÉTRIQUE: {score}%")
        
        # Vérification des propriétés biométriques
        if score > 100:
            print("  ❌ ERREUR: Score > 100% (Impossible en biométrie)")
        elif score == 100 and p1 != p2:
            print("  ⚠️ ALERTE: 100% pour deux fichiers différents (rare)")
            
    # Cas 1: Même personne
    run_case(img1_path, img2_path, "Genuine Pair (Même Personne)")
    
    # Cas 2: Personnes différentes
    run_case(img1_path, img3_path, "Impostor Pair (Personnes Différentes)")
    
    # Cas 3: Même fichier
    run_case(img1_path, img1_path, "Same File (Même fichier)")

if __name__ == "__main__":
    test_manual_pipeline()
