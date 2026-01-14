#librairie principale du jeu

from collections.abc import Callable
from typing import List, Optional
import pygame

# Variable globale pour compter les frames
loops = 0


class Scene:
    """
    Classe principale qui gère la fenêtre, la boucle de jeu et le rendu.
    
    width, height : dimensions de la fenêtre
    init : fonction appelée au démarrage pour créer les objets
    prepaint : fonction appelée avant chaque rendu
    tick : FPS cible (60 par défaut)
    """
    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        init: Optional[Callable[["Scene"], List]] = None,
        controller: Optional[Callable[[List, pygame.event.Event], bool]] = None,
        prepaint: Optional[Callable[["Scene"], bool]] = None,
        tick=60,
    ) -> None:
        # Initialisation de pygame
        pygame.init()
        pygame.mixer.init()
        
        # Configuration du temps
        self.clock = pygame.time.Clock()
        self.tick = tick  # FPS cible
        self.time_game: float = 0.0  # Temps total écoulé
        
        # Création de la fenêtre
        self.window_size = width, height
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Guts Training - Dithering Demo")
        
        # Objets du jeu (pour l'instant vide)
        self.objects: List = []
        if init is not None:
            self.objects = init(self)
        
        # Callbacks optionnels
        self.prepaint = prepaint
        self.controller = controller

    def mainloop(self) -> bool:
        """
        Boucle principale du jeu. Retourne False si on doit quitter.
        
        Étapes :
        1. Gérer les événements (fermeture, clavier, etc.)
        2. Appeler prepaint si défini (pour dessiner le fond)
        3. Mettre à jour l'affichage
        4. Réguler les FPS
        """
        global loops
        
        # 1. GESTION DES ÉVÉNEMENTS
        for event in pygame.event.get():
            # Bouton fermer la fenêtre
            if event.type == pygame.QUIT:
                return False
            
            # Touche ECHAP pour quitter
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            
            # Si un controller personnalisé est défini
            if self.controller:
                if not self.controller(self.objects, event):
                    return False
        
        # 2. RENDU
        # Efface l'écran en noir par défaut
        self.screen.fill((0, 0, 0))
        
        # Appelle la fonction de dessin personnalisée si elle existe
        if self.prepaint:
            if not self.prepaint(self):
                return False
        
        # 3. AFFICHAGE
        pygame.display.flip()  # Met à jour l'écran
        
        # 4. GESTION DU TEMPS
        elapsed = self.clock.tick(self.tick)  # Limite à self.tick FPS
        self.time_game += elapsed / 1000.0  # Convertit ms en secondes
        loops += 1
        
        return True  # Continue la boucle
    
    # ============================================
# PALETTE LIMITÉE - 24 couleurs total
# ============================================

# SECTION 1 : CIEL (6 couleurs)
# De l'horizon (clair) vers le haut (foncé)
SKY_COLORS = [
    (220, 240, 255),  # 0 - Blanc horizon (le plus clair)
    (180, 220, 245),  # 1 - Bleu très clair
    (135, 206, 235),  # 2 - Bleu ciel classique
    (100, 170, 210),  # 3 - Bleu moyen
    (70, 140, 190),   # 4 - Bleu profond
    (50, 100, 160),   # 5 - Bleu nuit (le plus foncé)
]
# Avec dithering entre ces 6 = ~15 nuances de bleu visibles !

# SECTION 2 : SOLEIL (4 couleurs)
SUN_COLORS = [
    (255, 250, 200),  # 6 - Blanc chaud (centre)
    (255, 230, 120),  # 7 - Jaune clair
    (255, 200, 80),   # 8 - Jaune-orange
    (240, 160, 60),   # 9 - Orange foncé (bord)
]
# Halo avec gradient dithéré du centre vers l'extérieur

# SECTION 3 : SOL/TERRE (5 couleurs)
GROUND_COLORS = [
    (180, 140, 100),  # 10 - Terre claire
    (150, 110, 80),   # 11 - Terre moyenne
    (120, 80, 60),    # 12 - Terre sombre
    (90, 60, 45),     # 13 - Terre très sombre
    (60, 40, 30),     # 14 - Ombres profondes
]
# Texture du sol avec variation

# SECTION 4 : ARBRE (4 couleurs)
TREE_COLORS = [
    (140, 100, 60),   # 15 - Bois clair (lumière)
    (100, 70, 40),    # 16 - Bois moyen
    (70, 50, 30),     # 17 - Bois sombre
    (40, 30, 20),     # 18 - Écorce/ombres
]

# SECTION 5 : NEIGE (3 couleurs)
SNOW_COLORS = [
    (255, 255, 255),  # 19 - Blanc pur
    (230, 235, 245),  # 20 - Blanc bleuté (ombres)
    (200, 210, 220),  # 21 - Gris clair neigeux
]

# SECTION 6 : GUTS (2 couleurs pour l'instant)
GUTS_COLORS = [
    (60, 60, 70),     # 22 - Armure sombre
    (40, 40, 45),     # 23 - Ombres armure
]

# ============================================
# PALETTE COMPLÈTE (pour référence)
# ============================================
FULL_PALETTE = (
    SKY_COLORS + 
    SUN_COLORS + 
    GROUND_COLORS + 
    TREE_COLORS + 
    SNOW_COLORS + 
    GUTS_COLORS
)

print(f"Nombre total de couleurs : {len(FULL_PALETTE)}")
# Affiche : 24


# ============================================
# ALGORITHME DE DITHERING
# ============================================

# Matrice de Bayer 4×4 (seuils de 0 à 15)
# Plus la valeur est haute, plus on favorise la couleur claire
BAYER_MATRIX_4x4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]

def color_distance(c1, c2):
    """
    Calcule la distance entre 2 couleurs RGB.
    
    Utilise la distance euclidienne :
    distance = √((r2-r1)² + (g2-g1)² + (b2-b1)²)
    
    Plus la distance est petite, plus les couleurs sont proches.
    """
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return ((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2) ** 0.5


def find_closest_colors(target_color, palette):
    """
    Trouve les 2 couleurs les plus proches d'une couleur cible dans la palette.
    
    Args:
        target_color: (R, G, B) - La couleur qu'on veut approcher
        palette: Liste de couleurs (R, G, B)
    
    Returns:
        (color1, color2, ratio) où :
        - color1 : couleur la plus proche
        - color2 : deuxième couleur la plus proche
        - ratio : proportion de color1 vs color2 (0.0 à 1.0)
    
    Exemple :
        target = (150, 180, 200)
        palette = [(100, 150, 180), (200, 210, 220)]
        → color1 = (100, 150, 180)
        → color2 = (200, 210, 220)
        → ratio = 0.6 (60% color1, 40% color2)
    """
    # Calcule toutes les distances
    distances = [(color_distance(target_color, c), c) for c in palette]
    
    # Trie par distance croissante
    distances.sort(key=lambda x: x[0])
    
    # Les 2 couleurs les plus proches
    closest_color = distances[0][1]
    second_closest_color = distances[1][1]
    
    # Calcul du ratio pour savoir quelle proportion de chaque couleur utiliser
    dist1 = distances[0][0]
    dist2 = distances[1][0]
    
    # Si les distances sont égales, ratio = 0.5
    # Si dist1 = 0 (couleur exacte), ratio = 1.0
    if dist1 + dist2 == 0:
        ratio = 1.0
    else:
        # Plus dist1 est petit par rapport à dist2, plus ratio est grand
        ratio = dist2 / (dist1 + dist2)
    
    return closest_color, second_closest_color, ratio


def dither_pixel(x, y, target_color, palette):
    """
    Applique le dithering ordonné (Bayer) pour un pixel donné.
    
    Args:
        x, y: Position du pixel à l'écran
        target_color: (R, G, B) - Couleur désirée
        palette: Liste de couleurs disponibles
    
    Returns:
        (R, G, B) - Couleur de la palette à utiliser pour ce pixel
    
    PRINCIPE DU DITHERING :
    
    1. On veut une couleur qui n'est PAS dans la palette (ex: gris moyen)
    2. On trouve les 2 couleurs les plus proches (ex: noir et blanc)
    3. On calcule le ratio (ex: 50% noir, 50% blanc = gris moyen)
    4. On utilise la matrice de Bayer pour décider quelle couleur mettre
    
    EXEMPLE VISUEL :
    
    Pour faire du gris moyen (50%) avec noir/blanc :
    
    Matrice Bayer 4×4 (normalisée 0-1) :
    ┌──────────────────┐
    │ 0.0  0.5  0.12 0.6│  Si ratio > valeur → couleur claire
    │ 0.75 0.25 0.87 0.4│  Sinon → couleur foncée
    │ 0.18 0.68 0.06 0.5│
    │ 0.93 0.43 0.81 0.3│
    └──────────────────┘
    
    Avec ratio=0.5 (50% blanc) :
    ┌──────────────────┐
    │ B    W    B    W │  B=noir, W=blanc
    │ W    B    W    B │  Pattern en damier
    │ B    W    B    B │  = Illusion de gris !
    │ W    B    W    B │
    └──────────────────┘
    """
    # 1. Trouve les 2 couleurs les plus proches
    color1, color2, ratio = find_closest_colors(target_color, palette)
    
    # 2. Récupère le seuil de Bayer pour cette position
    bayer_x = x % 4  # Module 4 pour répéter la matrice
    bayer_y = y % 4
    threshold = BAYER_MATRIX_4x4[bayer_y][bayer_x] / 16.0  # Normalise 0-15 → 0.0-1.0
    
    # 3. Compare le ratio au seuil pour choisir la couleur
    if ratio > threshold:
        return color1  # Couleur la plus proche
    else:
        return color2  # Deuxième couleur la plus proche


def dither_gradient(x, y, color_start, color_end, gradient_start, gradient_end, palette):
    """
    Crée un gradient dithéré entre 2 couleurs sur une plage de coordonnées.
    
    Args:
        x, y: Position du pixel
        color_start: (R, G, B) - Couleur au début du gradient
        color_end: (R, G, B) - Couleur à la fin du gradient
        gradient_start: Position de début (ex: y=0 pour gradient vertical)
        gradient_end: Position de fin (ex: y=280)
        palette: Liste de couleurs disponibles
    
    Returns:
        (R, G, B) - Couleur dithérée
    
    EXEMPLE POUR LE CIEL :
    
    gradient_start = 0 (haut de l'écran)
    gradient_end = 280 (bas du ciel)
    color_start = (50, 100, 160) - Bleu foncé en haut
    color_end = (220, 240, 255) - Blanc horizon en bas
    
    À y=0 → couleur = bleu foncé
    À y=140 → couleur = mélange 50/50
    À y=280 → couleur = blanc horizon
    
    Ensuite, dither_pixel() trouve les 2 couleurs de palette
    les plus proches et crée le pattern.
    """
    # 1. Calcule la position dans le gradient (0.0 à 1.0)
    if gradient_end - gradient_start == 0:
        t = 0.0
    else:
        t = (y - gradient_start) / (gradient_end - gradient_start)
        t = max(0.0, min(1.0, t))  # Limite entre 0 et 1
    
    # 2. Interpole linéairement entre color_start et color_end
    r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
    g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
    b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
    
    target_color = (r, g, b)
    
    # 3. Applique le dithering sur cette couleur interpolée
    return dither_pixel(x, y, target_color, palette)