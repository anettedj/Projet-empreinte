import numpy as np
import cv2

def manual_grayscale(img_bgr):
    """
    Convertit manuellement une image BGR en niveaux de gris.
    Formule: Y = 0.299*R + 0.587*G + 0.114*B
    """
    # OpenCV charge en BGR
    # img_bgr[:,:,0] -> Blue
    # img_bgr[:,:,1] -> Green
    # img_bgr[:,:,2] -> Red
    blue = img_bgr[:, :, 0].astype(np.float32)
    green = img_bgr[:, :, 1].astype(np.float32)
    red = img_bgr[:, :, 2].astype(np.float32)
    
    gray = 0.299 * red + 0.587 * green + 0.114 * blue
    return gray.astype(np.uint8)

def manual_median_filter(img, size=3):
    """
    Applique manuellement un filtre médian pour supprimer le bruit.
    """
    rows, cols = img.shape
    pad = size // 2
    # Créer une image de sortie
    output = np.zeros_like(img)
    # Ajouter un padding pour gérer les bords
    padded_img = np.pad(img, pad, mode='edge')
    
    for i in range(rows):
        for j in range(cols):
            # Extraire le voisinage
            window = padded_img[i:i+size, j:j+size]
            # Trier et prendre la médiane
            output[i, j] = np.median(window)
            
    return output

def manual_binarize(img, threshold=None, invert=True):
    """
    Convertit l'image en Noir et Blanc (Binaire).
    invert=True: considère que les crêtes sont plus sombres que le fond (standard FVC).
    """
    if threshold is None:
        # Otsu simplifié : utiliser la moyenne
        threshold = np.mean(img)
    
    if invert:
        binary = np.where(img < threshold, 255, 0).astype(np.uint8)
    else:
        binary = np.where(img >= threshold, 255, 0).astype(np.uint8)
    return binary

def manual_thinning(binary):
    """
    Amincissement (Squelettisation) selon l'algorithme de Zhang-Suen.
    binary : image binaire (0 ou 255)
    """
    img = binary.copy()
    img = img // 255  # Normaliser à 0 et 1
    
    rows, cols = img.shape
    changed = True
    
    while changed:
        changed = False
        pixels_to_remove = []
        
        # Sous-étape 1
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if img[i, j] != 1: continue
                
                P2, P3, P4 = img[i-1, j], img[i-1, j+1], img[i, j+1]
                P5, P6, P7 = img[i+1, j+1], img[i+1, j], img[i+1, j-1]
                P8, P9 = img[i, j-1], img[i-1, j-1]
                
                neighbors = [P2, P3, P4, P5, P6, P7, P8, P9]
                B = sum(neighbors)
                A = 0
                for k in range(8):
                    if neighbors[k] == 0 and neighbors[(k + 1) % 8] == 1:
                        A += 1
                
                if (2 <= B <= 6) and (A == 1) and (P2 * P4 * P6 == 0) and (P4 * P6 * P8 == 0):
                    pixels_to_remove.append((i, j))
        
        if pixels_to_remove:
            changed = True
            for i, j in pixels_to_remove: img[i, j] = 0
            
        pixels_to_remove = []
        
        # Sous-étape 2
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if img[i, j] != 1: continue
                
                P2, P3, P4 = img[i-1, j], img[i-1, j+1], img[i, j+1]
                P5, P6, P7 = img[i+1, j+1], img[i+1, j], img[i+1, j-1]
                P8, P9 = img[i, j-1], img[i-1, j-1]
                
                neighbors = [P2, P3, P4, P5, P6, P7, P8, P9]
                B = sum(neighbors)
                A = 0
                for k in range(8):
                    if neighbors[k] == 0 and neighbors[(k + 1) % 8] == 1:
                        A += 1
                
                if (2 <= B <= 6) and (A == 1) and (P2 * P4 * P8 == 0) and (P2 * P6 * P8 == 0):
                    pixels_to_remove.append((i, j))
        
        if pixels_to_remove:
            changed = True
            for i, j in pixels_to_remove: img[i, j] = 0
            
    return (img * 255).astype(np.uint8)

def extract_minutiae(skeleton):
    """
    Extrait les minuties (terminaisons et bifurcations) à partir du squelette.
    Utilise la méthode du Crossing Number (CN).
    """
    rows, cols = skeleton.shape
    skel = skeleton // 255  # 0 et 1
    
    terminations = []
    bifurcations = []
    
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if skel[i, j] != 1: continue
            
            # Voisins (ordre horaire)
            # P9 P2 P3
            # P8 P1 P4
            # P7 P6 P5
            P2 = skel[i-1, j]
            P3 = skel[i-1, j+1]
            P4 = skel[i, j+1]
            P5 = skel[i+1, j+1]
            P6 = skel[i+1, j]
            P7 = skel[i+1, j-1]
            P8 = skel[i, j-1]
            P9 = skel[i-1, j-1]
            
            neighbors = [int(P2), int(P3), int(P4), int(int(P5)), int(P6), int(P7), int(P8), int(P9)]
            
            # Crossing Number
            cn = 0
            for k in range(8):
                cn += abs(neighbors[k] - neighbors[(k + 1) % 8])
            cn = 0.5 * cn
            
            if cn == 1:
                terminations.append((j, i))  # (x, y)
            elif cn == 3:
                bifurcations.append((j, i)) # (x, y)
                
    return terminations, bifurcations

def manual_match(minutiae1, minutiae2, tolerance=10):
    """
    Compare deux ensembles de minuties manuellement.
    minutiae = (terminations, bifurcations)
    tolerance = distance maximale en pixels pour considérer un match.
    """
    term1, bif1 = minutiae1
    term2, bif2 = minutiae2
    
    if not term1 and not bif1: return 0.0, 0
    if not term2 and not bif2: return 0.0, 0

    # 1. Alignement par Centroïde (pour gérer la translation de base)
    def get_centroid(points):
        if not points: return (0, 0)
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)

    all1 = term1 + bif1
    all2 = term2 + bif2
    
    c1 = get_centroid(all1)
    c2 = get_centroid(all2)
    
    # Calcul du vecteur de translation
    dx = c1[0] - c2[0]
    dy = c1[1] - c2[1]
    
    # 2. Matching avec Bounding Box
    def count_matches(list1, list2, off_x, off_y):
        matches = 0
        matched_in_2 = set()
        for p1 in list1:
            for idx, p2 in enumerate(list2):
                if idx in matched_in_2: continue
                
                # Appliquer la translation à p2 pour le ramener vers p1
                p2_aligned = (p2[0] + off_x, p2[1] + off_y)
                
                dist = np.sqrt((p1[0] - p2_aligned[0])**2 + (p1[1] - p2_aligned[1])**2)
                if dist < tolerance:
                    matches += 1
                    matched_in_2.add(idx)
                    break
        return matches

    match_term = count_matches(term1, term2, dx, dy)
    match_bif = count_matches(bif1, bif2, dx, dy)
    
    total_matches = match_term + match_bif
    
    # Score : On normalise par rapport à la moyenne des points
    score = (2.0 * total_matches) / (len(all1) + len(all2)) * 100
    
    return round(score, 2), total_matches
