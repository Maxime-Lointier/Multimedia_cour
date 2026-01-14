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
    
    # ZONE 4 : SOL/TERRE (140px de haut)
    ground_color = (139, 90, 60)  # Marron terre
    pygame.draw.rect(screen, ground_color, (0, 280, width, 140))
    
    # ZONE 5 : ARBRE (placeholder rectangle)
    tree_color = (101, 67, 33)  # Marron foncé
    tree_rect = pygame.Rect(50, 220, 96, 200)  # x, y, largeur, hauteur
    pygame.draw.rect(screen, tree_color, tree_rect)
    
    # ZONE 6 : GUTS (placeholder rectangle)
    guts_color = (80, 80, 80)  # Gris foncé
    guts_rect = pygame.Rect(250, 260, 128, 160)
    pygame.draw.rect(screen, guts_color, guts_rect)
    
    # ZONE 7 : NEIGE AU SOL (60px de haut) - Texture détaillée
    if hasattr(scene, 'snow_ground') and scene.snow_ground is not None:
        screen.blit(scene.snow_ground, (0, 420))
    

    
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
    
    # Génère le sol enneigé avec texture
    scene.snow_ground = create_snow_ground(scene)
    
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

