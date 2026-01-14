# game.py - Base fonctionnelle avec zones de rendu

import pygame
from typing import List
import lib


def show_palette_test(screen):
    """
    Affiche toutes les couleurs de la palette pour vérifier.
    Chaque couleur = carré 30×30 pixels.
    """
    x, y = 10, 100
    
    for i, color in enumerate(lib.FULL_PALETTE):
        # Dessine un carré 30×30 par couleur
        pygame.draw.rect(screen, color, (x, y, 30, 30))
        
        # Bordure noire pour mieux voir
        pygame.draw.rect(screen, (0, 0, 0), (x, y, 30, 30), 1)
        
        # Numéro de la couleur
        font = pygame.font.Font(None, 16)
        num_text = font.render(str(i), True, (255, 255, 255))
        screen.blit(num_text, (x + 8, y + 8))
        
        # Passe à la ligne tous les 8 carrés
        x += 35
        if (i + 1) % 8 == 0:
            x = 10
            y += 35


def render_scene(scene: lib.Scene) -> bool:
    """
    Fonction de rendu appelée à chaque frame.
    Dessine toutes les zones de l'écran.
    
    Retourne True pour continuer, False pour quitter
    """
    screen = scene.screen
    width, height = scene.window_size
    
    # ZONE 1+2 : CIEL + COLLINE (pré-calculés, juste un blit !)
    if scene.static_background is not None:
        screen.blit(scene.static_background, (0, 0))
    
    # ZONE 3 : SOLEIL (cercle de 80px de diamètre)
    sun_color = (255, 220, 100)  # Jaune soleil
    sun_pos = (width - 120, 80)  # En haut à droite
    pygame.draw.circle(screen, sun_color, sun_pos, 40)
    
    # ZONE 4 : PLAN MOYEN TEXTURÉ (terre/herbe/neige avec dithering)
    if hasattr(scene, 'middle_ground') and scene.middle_ground is not None:
        screen.blit(scene.middle_ground, (0, 280))
    
    # Petite maison TRÈS lointaine (dessinée par-dessus le plan moyen)
    house_x = width - 120
    house_y = 345
    
    # Murs de la maison (gris foncé, très petit : 20×15)
    house_wall_color = (70, 75, 85)
    pygame.draw.rect(screen, house_wall_color, (house_x, house_y, 20, 15))
    
    # Toit pointu (noir)
    roof_color = (35, 35, 40)
    roof_points = [
        (house_x - 2, house_y),           # Gauche
        (house_x + 10, house_y - 12),     # Sommet pointu
        (house_x + 22, house_y)           # Droite
    ]
    pygame.draw.polygon(screen, roof_color, roof_points)
    
    # Cheminée (très petite)
    chimney_color = (50, 45, 45)
    pygame.draw.rect(screen, chimney_color, (house_x + 14, house_y - 8, 3, 5))
    
    # Fumée (petits pixels gris)
    smoke_color = (140, 145, 150)
    pygame.draw.circle(screen, smoke_color, (house_x + 16, house_y - 10), 1)
    pygame.draw.circle(screen, smoke_color, (house_x + 17, house_y - 13), 1)
    
    # Fenêtre minuscule (jaune - lumière)
    window_color = (220, 200, 120)
    pygame.draw.rect(screen, window_color, (house_x + 8, house_y + 5, 4, 5))
    
    # Porte (marron très foncé)
    door_color = (40, 35, 30)
    pygame.draw.rect(screen, door_color, (house_x + 3, house_y + 7, 4, 8))
    
    # ZONE 5 : ARBRE HIVERNAL (arbre mature noir sans feuilles)
    if hasattr(scene, 'tree') and scene.tree is not None:
        # Position de l'arbre (à gauche de la scène, plus haut)
        screen.blit(scene.tree, (10, 70))  # x=10, y=70 pour un arbre très haut
    
    # ZONE 6 : GUTS (placeholder rectangle)
    guts_color = (80, 80, 80)  # Gris foncé
    guts_rect = pygame.Rect(250, 260, 128, 160)
    pygame.draw.rect(screen, guts_color, guts_rect)
    
    # ZONE 7 : NEIGE AU SOL (60px de haut) - Texture détaillée
    if hasattr(scene, 'snow_ground') and scene.snow_ground is not None:
        screen.blit(scene.snow_ground, (0, 420))
    
    # TEST DE LA PALETTE : Affiche les 24 couleurs
    #show_palette_test(screen) la palette disponible
    
    # AFFICHAGE DEBUG : Informations à l'écran
    font = pygame.font.Font(None, 24)
    fps_text = font.render(f"FPS: {int(scene.clock.get_fps())}", True, (255, 0, 0))
    time_text = font.render(f"Time: {scene.time_game:.1f}s", True, (255, 0, 0))
    frames_text = font.render(f"Frames: {lib.loops}", True, (255, 0, 0))
    
    screen.blit(fps_text, (10, 10))
    screen.blit(time_text, (10, 35))
    screen.blit(frames_text, (10, 60))
    
    return True  # Continue le jeu


def create_static_background(scene: lib.Scene):
    """
    Crée le background statique (ciel + colline) UNE SEULE FOIS.
    Cette surface sera réutilisée à chaque frame sans recalcul.
    """
    width, height = scene.window_size
    import math
    
    print("Génération du background statique (ciel + colline)...")
    
    # Crée une surface pour le background
    bg = pygame.Surface((width, 280))  # Hauteur du ciel + colline
    
    # ZONE 1 : CIEL HIVERNAL (280px de haut)
    sky_top = lib.SKY_COLORS[5]      # Gris-bleu foncé (haut)
    sky_bottom = lib.SKY_COLORS[0]   # Gris clair (horizon)
    
    # Dessine le ciel pixel par pixel avec dithering
    for y in range(280):
        for x in range(width):
            pixel_color = lib.dither_gradient(
                x, y,
                sky_top, sky_bottom,
                0, 280,
                lib.SKY_COLORS
            )
            bg.set_at((x, y), pixel_color)
    
    # ZONE 2 : MONTAGNES EN PLUSIEURS COUCHES (effet de profondeur)
    # Définition des montagnes : (centre_x, largeur, hauteur, couleur_idx)
    # couleur_idx: 0=plus clair (lointain), 2=plus foncé (proche)
    
    mountains = [
        # Arrière-plan (lointain, clair, plus larges)
        (width * 0.2, 200, 100, 0),   # Montagne gauche lointaine
        (width * 0.7, 250, 120, 0),   # Montagne droite lointaine
        
        # Plan moyen
        (width * 0.45, 180, 140, 1),  # Montagne centre
        (width * 0.85, 160, 110, 1),  # Montagne droite moyenne
        
        # Premier plan (proche, foncé, plus étroites et hautes)
        (width * 0.15, 120, 160, 2),  # Montagne gauche proche
        (width * 0.6, 140, 150, 2),   # Montagne droite proche
    ]
    
    mountain_base_y = 280  # Touche le sol maintenant
    
    # Dessine chaque montagne de l'arrière vers l'avant
    for center_x, mtn_width, mtn_height, color_depth in mountains:
        for x in range(width):
            # Distance normalisée du centre (-1 à 1)
            dx = (x - center_x) / (mtn_width / 2)
            
            if abs(dx) <= 1.0:  # Si on est dans la largeur de la montagne
                # Forme triangulaire/pointue : y = base - height * (1 - |x|)
                # Plus pointu que la parabole précédente
                peak_y = mountain_base_y - mtn_height * (1 - abs(dx))
                
                # Dessine du sommet jusqu'à la base
                for y in range(int(peak_y), mountain_base_y):
                    if 0 <= y < 280:  # Reste dans la zone ciel
                        # Gradient selon profondeur dans la montagne
                        # Choix de couleur selon la couche (lointain/proche)
                        if color_depth == 0:
                            # Lointain : très clair (effet brume)
                            top_color = lib.HILL_COLORS[0]
                            bottom_color = lib.HILL_COLORS[1]
                        elif color_depth == 1:
                            # Moyen
                            top_color = lib.HILL_COLORS[1]
                            bottom_color = lib.HILL_COLORS[2]
                        else:
                            # Proche : plus foncé
                            top_color = lib.HILL_COLORS[2]
                            bottom_color = (100, 110, 125)  # Encore plus foncé
                        
                        pixel_color = lib.dither_gradient(
                            x, y,
                            top_color,
                            bottom_color,
                            int(peak_y), mountain_base_y,
                            lib.HILL_COLORS
                        )
                        bg.set_at((x, y), pixel_color)
    
    print("Background statique généré !")
    return bg


def create_middle_ground(scene: lib.Scene):
    """
    Crée le plan moyen : SOL D'HERBE avec patches de terre et neige.
    Base = herbe sèche, avec zones irrégulières de terre nue et neige.
    """
    width = scene.window_size[0]
    import random
    import math
    
    print("Génération du plan moyen naturel (herbe/terre/neige)...")
    
    # Surface pour le plan moyen (140px de haut)
    mg_surface = pygame.Surface((width, 140))
    
    # 1. REMPLIR LA BASE AVEC DE L'HERBE
    random.seed(42)
    
    for y in range(140):
        for x in range(width):
            # Variation subtile de l'herbe (différentes nuances)
            noise = random.random()
            
            if noise > 0.7:
                target = lib.GRASS_COLORS[0]  # Herbe claire
            elif noise > 0.4:
                target = lib.GRASS_COLORS[1]  # Herbe moyenne
            elif noise > 0.2:
                target = lib.GRASS_COLORS[2]  # Herbe foncée
            else:
                target = lib.GRASS_COLORS[3]  # Herbe très sombre
            
            pixel_color = lib.dither_pixel(x, y, target, lib.GRASS_COLORS)
            mg_surface.set_at((x, y), pixel_color)
    
    # 2. AJOUTER DES PATCHES DE TERRE (zones sans herbe)
    random.seed(123)
    num_dirt_patches = 12  # 12 zones de terre
    
    for _ in range(num_dirt_patches):
        # Position et taille aléatoires
        patch_x = random.randint(0, width)
        patch_y = random.randint(0, 140)
        patch_size = random.randint(25, 60)
        
        # Dessiner un patch irrégulier
        for dy in range(-patch_size, patch_size):
            for dx in range(-patch_size, patch_size):
                px = patch_x + dx
                py = patch_y + dy
                
                if 0 <= px < width and 0 <= py < 140:
                    # Distance du centre (forme organique)
                    dist = math.sqrt(dx**2 + dy**2) / patch_size
                    
                    # Forme irrégulière avec bruit
                    random.seed(px * 100 + py)
                    noise_factor = random.random() * 0.3
                    
                    if dist + noise_factor < 0.9:  # Bordures irrégulières
                        # Couleur de terre selon distance du centre
                        if dist < 0.3:
                            target = lib.GROUND_COLORS[2]  # Terre sombre (centre)
                        elif dist < 0.6:
                            target = lib.GROUND_COLORS[1]  # Terre moyenne
                        else:
                            target = lib.GROUND_COLORS[0]  # Terre claire (bords)
                        
                        pixel_color = lib.dither_pixel(px, py, target, lib.GROUND_COLORS)
                        mg_surface.set_at((px, py), pixel_color)
    
    # 3. AJOUTER DES PATCHES DE NEIGE (asymétriques)
    random.seed(456)
    num_snow_patches = 8  # 8 zones de neige
    
    for _ in range(num_snow_patches):
        # Position et taille aléatoires
        patch_x = random.randint(0, width)
        patch_y = random.randint(0, 140)
        patch_w = random.randint(30, 70)
        patch_h = random.randint(20, 50)
        
        # Forme asymétrique (ellipse déformée)
        for dy in range(-patch_h, patch_h):
            for dx in range(-patch_w, patch_w):
                px = patch_x + dx
                py = patch_y + dy
                
                if 0 <= px < width and 0 <= py < 140:
                    # Distance normalisée (ellipse)
                    dist_x = abs(dx) / patch_w
                    dist_y = abs(dy) / patch_h
                    dist = math.sqrt(dist_x**2 + dist_y**2)
                    
                    # Déformation asymétrique
                    random.seed(px * 50 + py)
                    asymmetry = random.random() * 0.4 - 0.2
                    
                    if dist + asymmetry < 0.85:  # Bordures organiques
                        # Couleur de neige selon distance
                        if dist < 0.4:
                            target = lib.SNOW_COLORS[0]  # Blanc pur (centre)
                        elif dist < 0.7:
                            target = lib.SNOW_COLORS[1]  # Blanc bleuté
                        else:
                            target = lib.SNOW_COLORS[2]  # Gris clair (bords fondus)
                        
                        pixel_color = lib.dither_pixel(px, py, target, lib.SNOW_COLORS)
                        mg_surface.set_at((px, py), pixel_color)
    
    print("Plan moyen naturel généré !")
    return mg_surface


def create_snow_ground(scene: lib.Scene):
    """
    Crée le sol enneigé avec texture détaillée.
    La neige n'est pas uniforme : variations de lumière, ombres, aspérités.
    """
    width, height = scene.window_size
    import random
    
    print("Génération du sol enneigé avec texture...")
    
    # Surface pour le sol (60px de haut)
    snow_surface = pygame.Surface((width, 60))
    
    # Générateur de bruit pour texture organique
    random.seed(42)  # Seed fixe pour cohérence
    
    for y in range(60):
        for x in range(width):
            # Variation de base selon la position verticale
            # Plus on descend, plus c'est sombre (ombre/profondeur)
            base_brightness = 1.0 - (y / 60) * 0.3  # De 1.0 à 0.7
            
            # Ajout de bruit pour texture granuleuse de neige
            noise = (random.random() - 0.5) * 0.4  # -0.2 à +0.2
            
            # Bruit supplémentaire à plus grande échelle (bosses/creux)
            import math
            wave_x = math.sin(x / 20.0) * 0.1
            wave_y = math.cos(y / 10.0) * 0.1
            
            # Combinaison des variations
            brightness = base_brightness + noise + wave_x + wave_y
            brightness = max(0.0, min(1.0, brightness))  # Clamp 0-1
            
            # Choix de la couleur selon la luminosité
            if brightness > 0.8:
                target = lib.SNOW_COLORS[0]  # Blanc pur (zones éclairées)
            elif brightness > 0.5:
                target = lib.SNOW_COLORS[1]  # Blanc bleuté (normal)
            else:
                target = lib.SNOW_COLORS[2]  # Gris clair (ombres)
            
            # Applique le dithering pour transitions douces
            pixel_color = lib.dither_pixel(x, y, target, lib.SNOW_COLORS)
            snow_surface.set_at((x, y), pixel_color)
    
    print("Sol enneigé généré !")
    return snow_surface
    """
    Crée le sol enneigé avec texture détaillée.
    La neige n'est pas uniforme : variations de lumière, ombres, aspérités.
    """
    width, height = scene.window_size
    import random
    
    print("Génération du sol enneigé avec texture...")
    
    # Surface pour le sol (60px de haut)
    snow_surface = pygame.Surface((width, 60))
    
    # Générateur de bruit pour texture organique
    random.seed(42)  # Seed fixe pour cohérence
    
    for y in range(60):
        for x in range(width):
            # Variation de base selon la position verticale
            # Plus on descend, plus c'est sombre (ombre/profondeur)
            base_brightness = 1.0 - (y / 60) * 0.3  # De 1.0 à 0.7
            
            # Ajout de bruit pour texture granuleuse de neige
            noise = (random.random() - 0.5) * 0.4  # -0.2 à +0.2
            
            # Bruit supplémentaire à plus grande échelle (bosses/creux)
            import math
            wave_x = math.sin(x / 20.0) * 0.1
            wave_y = math.cos(y / 10.0) * 0.1
            
            # Combinaison des variations
            brightness = base_brightness + noise + wave_x + wave_y
            brightness = max(0.0, min(1.0, brightness))  # Clamp 0-1
            
            # Choix de la couleur selon la luminosité
            if brightness > 0.8:
                target = lib.SNOW_COLORS[0]  # Blanc pur (zones éclairées)
            elif brightness > 0.5:
                target = lib.SNOW_COLORS[1]  # Blanc bleuté (normal)
            else:
                target = lib.SNOW_COLORS[2]  # Gris clair (ombres)
            
            # Applique le dithering pour transitions douces
            pixel_color = lib.dither_pixel(x, y, target, lib.SNOW_COLORS)
            snow_surface.set_at((x, y), pixel_color)
    
    print("Sol enneigé généré !")
    return snow_surface


def draw_tree_branch(surface, x, y, angle, length, thickness, depth, max_depth, side_bias=0):
    """
    Dessine une branche d'arbre de manière récursive avec asymétrie.
    
    Args:
        surface: Surface sur laquelle dessiner
        x, y: Point de départ de la branche
        angle: Angle de la branche (en degrés)
        length: Longueur de la branche
        thickness: Épaisseur de la branche
        depth: Profondeur actuelle de récursion
        max_depth: Profondeur maximale (nombre de divisions)
        side_bias: Biais d'asymétrie (-1 à 1, influence la direction)
    """
    import math
    import random
    
    if depth > max_depth or length < 2:
        return
    
    # Calcul du point final de la branche
    rad = math.radians(angle)
    end_x = x + length * math.cos(rad)
    end_y = y - length * math.sin(rad)  # - car y augmente vers le bas
    
    # Choix de couleur selon l'épaisseur
    if thickness > 10:
        color = lib.TREE_COLORS[0]  # Tronc principal (gris-noir)
    elif thickness > 5:
        color = lib.TREE_COLORS[1]  # Branches moyennes (noir)
    else:
        color = lib.TREE_COLORS[3]  # Branches fines (noir profond)
    
    # Dessine la branche (ligne épaisse)
    pygame.draw.line(surface, color, (int(x), int(y)), (int(end_x), int(end_y)), max(1, int(thickness)))
    
    # Récursion : créer des sous-branches avec asymétrie
    if depth < max_depth:
        # Angle de divergence avec variation
        base_spread = 20 if depth < 2 else 30
        angle_spread_left = base_spread + random.randint(-5, 10)
        angle_spread_right = base_spread + random.randint(-5, 10)
        
        # Réduction de longueur et épaisseur avec variation
        length_factor = 0.65 + random.random() * 0.15  # 0.65 à 0.8
        new_thickness = thickness * 0.7
        
        # Asymétrie : une branche peut être plus longue/forte que l'autre
        left_length = length * length_factor * (1.0 + side_bias * 0.3)
        right_length = length * length_factor * (1.0 - side_bias * 0.3)
        
        # Décide si on crée la branche gauche (asymétrie)
        if random.random() > 0.1:  # 90% de chance
            new_bias = side_bias + random.uniform(-0.2, 0.3)
            draw_tree_branch(surface, end_x, end_y, angle + angle_spread_left, 
                            left_length, new_thickness, depth + 1, max_depth, new_bias)
        
        # Décide si on crée la branche droite (asymétrie)
        if random.random() > 0.1:  # 90% de chance
            new_bias = side_bias + random.uniform(-0.3, 0.2)
            draw_tree_branch(surface, end_x, end_y, angle - angle_spread_right, 
                            right_length, new_thickness, depth + 1, max_depth, new_bias)
        
        # Branche centrale occasionnelle (pour densité)
        if depth < 4 and random.random() > 0.6:
            draw_tree_branch(surface, end_x, end_y, angle + random.randint(-10, 10), 
                            length * 0.6, new_thickness * 0.8, depth + 1, max_depth, side_bias)


def create_tree(scene: lib.Scene):
    """
    Crée un arbre mature noir hivernal sans feuilles.
    Grand, asymétrique et imposant.
    """
    import random
    
    print("Génération de l'arbre hivernal...")
    
    # Surface plus grande pour un arbre imposant
    tree_surface = pygame.Surface((300, 350), pygame.SRCALPHA)
    
    # Seed pour cohérence mais avec variation
    random.seed(123)
    
    # Position de départ (base du tronc)
    base_x = 80  # Un peu à gauche pour l'asymétrie
    base_y = 350  # Bas de la surface
    
    # Dessine le tronc principal puis les branches récursivement
    # Arbre plus grand et asymétrique
    draw_tree_branch(
        tree_surface,
        x=base_x,
        y=base_y,
        angle=88,          # Légèrement incliné (asymétrique)
        length=100,        # Tronc plus long (était 60)
        thickness=18,      # Tronc plus épais (était 12)
        depth=0,
        max_depth=7,       # Plus de niveaux = plus de branches
        side_bias=0.3      # Biais vers la droite
    )
    
    print("Arbre hivernal généré !")
    return tree_surface


def game_init(scene: lib.Scene) -> List:
    """
    Fonction d'initialisation appelée au démarrage.
    Pré-calcule les éléments statiques.
    """
    width = scene.window_size[0]
    height = scene.window_size[1]
    
    print("=== INITIALISATION DU JEU ===")
    print(f"Résolution : {width}×{height}")
    print(f"FPS cible : {scene.tick}")
    print("Appuyez sur ECHAP pour quitter")
    print("============================")
    
    # Génère le background statique UNE SEULE FOIS
    scene.static_background = create_static_background(scene)
    
    # Génère le plan moyen texturé (terre/herbe/neige)
    scene.middle_ground = create_middle_ground(scene)
    
    # Génère le sol enneigé avec texture
    scene.snow_ground = create_snow_ground(scene)
    
    # Génère l'arbre hivernal
    scene.tree = create_tree(scene)
    
    objects = []
    return objects


# DÉMARRAGE DU JEU
game = lib.Scene(
    width=640, 
    height=480, 
    init=game_init,
    prepaint=render_scene,  # ← Important ! Lie la fonction de rendu
    tick=60
)

# Boucle principale
RUN = True
while RUN:
    RUN = game.mainloop()

# Affichage des stats finales
print(f"\n=== FIN DU JEU ===")
print(f"Fenêtre fermée après {lib.loops} frames")
print(f"Durée totale : {game.time_game:.2f}s")
print(f"FPS moyen : {lib.loops / game.time_game:.1f}")

