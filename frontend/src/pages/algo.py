import numpy as np

def zhang_suen_thinning(binary):
    """
    Thinning (amincissement) selon Zhang–Suen
    binary : image binaire (0 = fond, 255 = crêtes)
    return : image squelette (crêtes d'un pixel)
    """

    # Copie de l'image pour ne pas modifier l'originale
    img = binary.copy()

    # Normalisation : 0 = fond, 1 = objet
    img[img > 0] = 1

    # Indique si l'image a encore été modifiée
    changed = True

    # Boucle principale : répéter jusqu'à ce qu'aucun pixel ne soit supprimé
    while changed:
        changed = False
        pixels_to_remove = []

        # SOUS-ÉTAPE 1
        for i in range(1, img.shape[0] - 1):
            for j in range(1, img.shape[1] - 1):

                P1 = img[i, j]

                # Choix : traiter uniquement les pixels blancs (objets)
                if P1 != 1:
                    continue

                # Définition des 8 voisins autour du pixel (sens horaire)
                # Choix : 8 voisins pour préserver la connectivité
                P2 = img[i-1, j]
                P3 = img[i-1, j+1]
                P4 = img[i, j+1]
                P5 = img[i+1, j+1]
                P6 = img[i+1, j]
                P7 = img[i+1, j-1]
                P8 = img[i, j-1]
                P9 = img[i-1, j-1]

                neighbors = [P2, P3, P4, P5, P6, P7, P8, P9]

                # B : nombre de voisins blancs
                # Choix : conserver pixels avec 2 à 6 voisins
                # Pour ne pas supprimer les extrémités (<2) ni les pixels centraux (>6)
                B = sum(neighbors)

                # A : nombre de transitions 0 → 1 autour de P1
                # Choix : A == 1 pour ne supprimer que des pixels qui ne coupent pas la connectivité
                A = sum(
                    (neighbors[k] == 0 and neighbors[(k + 1) % 8] == 1)
                    for k in range(8)
                )

                # Conditions pour supprimer le pixel
                # Choix : conditions multiplicatives pour protéger jonctions et bifurcations
                if (
                    2 <= B <= 6 and       # Choix 4 : préserver extrémités et pixels centraux
                    A == 1 and            # Choix 5 : préserver connectivité
                    P2 * P4 * P6 == 0 and # Choix 6 : ne pas supprimer pixel si P2,P4,P6 sont tous blancs (jonction)
                    P4 * P6 * P8 == 0     # Même idée : protéger bifurcation
                ):
                    pixels_to_remove.append((i, j))

        # Supprimer les pixels marqués
        if pixels_to_remove:
            changed = True
            for i, j in pixels_to_remove:
                img[i, j] = 0

        pixels_to_remove = []

        # SOUS-ÉTAPE 2
        for i in range(1, img.shape[0] - 1):
            for j in range(1, img.shape[1] - 1):

                P1 = img[i, j]
                if P1 != 1:   # Même choix : ne traiter que l'objet
                    continue

                P2 = img[i-1, j]
                P3 = img[i-1, j+1]
                P4 = img[i, j+1]
                P5 = img[i+1, j+1]
                P6 = img[i+1, j]
                P7 = img[i+1, j-1]
                P8 = img[i, j-1]
                P9 = img[i-1, j-1]

                neighbors = [P2, P3, P4, P5, P6, P7, P8, P9]

                B = sum(neighbors)
                A = sum(
                    (neighbors[k] == 0 and neighbors[(k + 1) % 8] == 1)
                    for k in range(8)
                )

                # Sous-étape 2 : conditions légèrement différentes pour équilibrer amincissement
                if (
                    2 <= B <= 6 and      # Choix 4 : protéger extrémités et pixels centraux
                    A == 1 and           # Choix 5 : préserver connectivité
                    P2 * P4 * P8 == 0 and # Choix 6 : protéger jonctions
                    P2 * P6 * P8 == 0
                ):
                    pixels_to_remove.append((i, j))

        # Suppression finale de l'itération
        if pixels_to_remove:
            changed = True
            for i, j in pixels_to_remove:
                img[i, j] = 0

    # Retour à 0 / 255 pour image classique
    return img * 255
