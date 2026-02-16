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
    
    # Si l'image est déjà en niveaux de gris (2D), on la retourne telle quelle
    if len(img_bgr.shape) == 2:
        return img_bgr.astype(np.uint8)
        
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

def manual_gabor(img):
    """
    Applique un filtre de Gabor pour renforcer les crêtes.
    Utilisation de float32 pour accumuler sans saturation.
    """
    gabor_accum = np.zeros_like(img, dtype=np.float32)
    
    for i in range(16):
        theta = np.pi * i / 16
        # Paramètres optimaux selon le code précédent de l'utilisateur
        kernel = cv2.getGaborKernel((31, 31), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
        fimg = cv2.filter2D(img, cv2.CV_32F, kernel)
        np.maximum(gabor_accum, fimg, gabor_accum)
        
    # Normalisation pour éviter l'effet "écran de TV cassé" (overflow/saturation)
    result = cv2.normalize(gabor_accum, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    return result

def manual_binarize(img, invert=True):
    """
    Convertit l'image en Binaire avec seuillage adaptatif.
    Plus robuste aux variations d'illumination que le seuillage global.
    """
    # Flou gaussien pour lisser les crêtes avant binarisation
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Utilisation d'OpenCV pour le seuillage adaptatif (mais on reste dans l'esprit "manuel" du pipeline)
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    if invert:
        binary = cv2.bitwise_not(binary)
        
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
    
    raw_terminations = []
    raw_bifurcations = []
    
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if skel[i, j] != 1: continue
            
            # Voisins (ordre horaire)
            P2, P3, P4 = skel[i-1, j], skel[i-1, j+1], skel[i, j+1]
            P5, P6, P7 = skel[i+1, j+1], skel[i+1, j], skel[i+1, j-1]
            P8, P9 = skel[i, j-1], skel[i-1, j-1]
            
            neighbors = [int(P2), int(P3), int(P4), int(P5), int(P6), int(P7), int(P8), int(P9)]
            
            cn = 0
            for k in range(8):
                cn += abs(neighbors[k] - neighbors[(k + 1) % 8])
            cn = 0.5 * cn
            
            if cn == 1:
                raw_terminations.append((j, i))  # (x, y)
            elif cn == 3:
                raw_bifurcations.append((j, i)) # (x, y)
    
    # --- Filtrage Avancé des Fausses Minuties ---
    # 1. Supprimer les minuties trop proches les unes des autres (bruit de squelettisation)
    def dist(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    filtered_term = []
    for i, t1 in enumerate(raw_terminations):
        keep = True
        for j, t2 in enumerate(raw_terminations):
            if i != j and dist(t1, t2) < 10: # Espacement standard
                keep = False
                break
        if keep: filtered_term.append(t1)
        
    filtered_bif = []
    for i, b1 in enumerate(raw_bifurcations):
        keep = True
        for j, b2 in enumerate(raw_bifurcations):
            if i != j and dist(b1, b2) < 10: # Espacement standard
                keep = False
                break
        if keep: filtered_bif.append(b1)
                
    return filtered_term, filtered_bif

def normalize_image(img, target_size=(300, 300)):
    """Normalise la taille et les valeurs de pixels."""
    img_resized = cv2.resize(img, target_size)
    # Normalisation Min-Max pour étendre la dynamique
    img_norm = cv2.normalize(img_resized, None, 0, 255, cv2.NORM_MINMAX)
    return img_norm

def enhance_contrast(img):
    """Améliore le contraste local avec CLAHE."""
    # CLAHE est plus efficace que l'égalisation d'histogramme globale pour les empreintes
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(img)

def segment_fingerprint(img, block_size=16, threshold_var=100):
    """
    Segmente l'empreinte pour isoler la région d'intérêt (ROI).
    Utilise la variance locale pour détecter les zones avec des crêtes.
    """
    rows, cols = img.shape
    mask = np.zeros((rows, cols), dtype=np.uint8)
    
    # Calculer la variance par blocs
    for i in range(0, rows - block_size + 1, block_size):
        for j in range(0, cols - block_size + 1, block_size):
            block = img[i:i+block_size, j:j+block_size]
            variance = np.var(block)
            
            # Si la variance est élevée, c'est une zone d'empreinte (Foregound)
            if variance > threshold_var:
                mask[i:i+block_size, j:j+block_size] = 255
    
    # Nettoyage du masque avec morphologie
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

def morphological_operations(binary):
    """
    Nettoie l'image binaire pour supprimer le bruit et combler les trous.
    """
    kernel = np.ones((3,3), np.uint8)
    # Ouverture : supprime les petits points blancs isolés
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    # Fermeture : comble les petits trous noirs dans les crêtes
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    return closing

def filter_border_minutiae(minutiae, img_shape, border=15):
    """
    Supprime les minuties détectées trop près des bords de l'image ou du masque.
    Elles sont souvent de faux positifs dus à la segmentation.
    """
    rows, cols = img_shape
    term, bif = minutiae
    
    def is_valid(p):
        x, y = p
        return border < x < cols - border and border < y < rows - border
    
    f_term = [p for p in term if is_valid(p)]
    f_bif = [p for p in bif if is_valid(p)]
    
    return f_term, f_bif

def complete_preprocessing_pipeline(img_bgr):
    """
    Pipeline complet de prétraitement biométrique (10 étapes).
    """
    # 1. Conversion en niveaux de gris
    gray = manual_grayscale(img_bgr)
    
    # 2. Normalisation (taille et dynamique)
    norm = normalize_image(gray)
    
    # 3. Amélioration contraste (CLAHE)
    enhanced = enhance_contrast(norm)
    
    # 4. Segmentation (ROI)
    mask = segment_fingerprint(enhanced)
    
    # 5. Application du masque
    segmented = cv2.bitwise_and(enhanced, enhanced, mask=mask)
    
    # 6. Filtrage du bruit (Médian)
    filtered = manual_median_filter(segmented)
    
    # 7. Renforcement des crêtes (Gabor) - Améliore l'EER
    gabor_enhanced = manual_gabor(filtered)
    
    # 8. Binarisation (Adaptative simplifiée)
    # On utilise maintenant l'image renforcée par Gabor
    binary = manual_binarize(gabor_enhanced, invert=True)
    
    # 9. Nettoyage morphologique
    cleaned = morphological_operations(binary)
    
    # 10. Squelettisation (Zhang-Suen)
    skeleton = manual_thinning(cleaned)
    
    # 11. Extraction des minuties (Crossing Number)
    raw_minutiae = extract_minutiae(skeleton)
    
    # 12. Filtrage des fausses minuties (bords)
    filtered_minutiae = filter_border_minutiae(raw_minutiae, skeleton.shape)
    
    return filtered_minutiae, skeleton

def manual_match(minutiae1, minutiae2, tolerance=8):
    """
    Matching robuste avec validation de voisinage et support de rotation légère.
    """
    term1, bif1 = minutiae1
    term2, bif2 = minutiae2
    all1 = term1 + bif1
    all2 = term2 + bif2
    
    if len(all1) < 5 or len(all2) < 5:
        return 0.0, 0

    def rotate_point(p, angle_deg, center=(150, 150)):
        if angle_deg == 0: return p
        angle_rad = np.radians(angle_deg)
        ox, oy = center
        px, py = p
        qx = ox + np.cos(angle_rad) * (px - ox) - np.sin(angle_rad) * (py - oy)
        qy = oy + np.sin(angle_rad) * (px - ox) + np.cos(angle_rad) * (py - oy)
        return (qx, qy)

    def get_neighbors(p, others, count=3):
        dists = [np.sqrt((p[0]-o[0])**2 + (p[1]-o[1])**2) for o in others if o != p]
        return sorted(dists)[:count]

    neigh1 = [get_neighbors(p, all1) for p in all1]
    
    best_matches = 0
    
    # Tester quelques angles
    for angle in [-5, 0, 5]:
        rot_all2 = [rotate_point(p, angle) for p in all2]
        rot_term2 = [rotate_point(p, angle) for p in term2]
        rot_bif2 = [rotate_point(p, angle) for p in bif2]
        neigh2 = [get_neighbors(p, rot_all2) for p in rot_all2]
        
        for i, p1 in enumerate(all1[:12]):
            for j, p2 in enumerate(rot_all2[:12]):
                n1, n2 = neigh1[i], neigh2[j]
                if len(n1) == len(n2) and len(n1) > 0:
                    sim = sum(1 for d1, d2 in zip(n1, n2) if abs(d1 - d2) < 5)
                    if sim < 1: continue 
                
                tx, ty = p1[0] - p2[0], p1[1] - p2[1]
                
                def count_valid(l1, lr2, ox, oy):
                    if not l1 or not lr2: return 0
                    pts1 = np.array(l1)
                    pts2_shifted = np.array(lr2) + np.array([ox, oy])
                    
                    # Distance matrix using broadcasting
                    # Shape: (len(pts1), len(pts2_shifted))
                    diff = pts1[:, np.newaxis, :] - pts2_shifted[np.newaxis, :, :]
                    dists = np.sqrt(np.sum(diff**2, axis=2))
                    
                    matches = 0
                    mask = dists < tolerance
                    used_in_2 = np.zeros(len(pts2_shifted), dtype=bool)
                    
                    for row in mask:
                        allowed = row & ~used_in_2
                        if np.any(allowed):
                            matches += 1
                            # Greedy match: take the first available
                            idx = np.where(allowed)[0][0]
                            used_in_2[idx] = True
                    return matches

                total = count_valid(term1, rot_term2, tx, ty) + count_valid(bif1, rot_bif2, tx, ty)
                if total > best_matches:
                    best_matches = total

    score = (2.0 * best_matches) / (len(all1) + len(all2)) * 100
    return round(score, 2), best_matches
