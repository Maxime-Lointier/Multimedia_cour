# game.py - Base fonctionnelle avec zones de rendu

import pygame
from typing import List
import lib


def render_scene(scene: lib.Scene) -> bool:
    """
    Fonction de rendu appelée à chaque frame.
    Dessine toutes les zones de l'écran.
    
    Retourne True pour continuer, False pour quitter
    """
    screen = scene.screen
    width, height = scene.window_size
    
    # ZONE 1 : CIEL (280px de haut)
    # Couleur unie pour l'instant, on ajoutera le dithering après
    sky_color = (135, 206, 235)  # Bleu ciel
    pygame.draw.rect(screen, sky_color, (0, 0, width, 280))
    
    # ZONE 2 : SOLEIL (cercle de 80px de diamètre)
    sun_color = (255, 220, 100)  # Jaune soleil
    sun_pos = (width - 120, 80)  # En haut à droite
    pygame.draw.circle(screen, sun_color, sun_pos, 40)
    
    # ZONE 3 : COLLINE/SOL (140px de haut)
    ground_color = (139, 90, 60)  # Marron terre
    pygame.draw.rect(screen, ground_color, (0, 280, width, 140))
    
    # ZONE 4 : ARBRE (placeholder rectangle)
    tree_color = (101, 67, 33)  # Marron foncé
    tree_rect = pygame.Rect(50, 220, 96, 200)  # x, y, largeur, hauteur
    pygame.draw.rect(screen, tree_color, tree_rect)
    
    # ZONE 5 : GUTS (placeholder rectangle)
    guts_color = (80, 80, 80)  # Gris foncé
    guts_rect = pygame.Rect(250, 260, 128, 160)
    pygame.draw.rect(screen, guts_color, guts_rect)
    
    # ZONE 6 : NEIGE AU SOL (60px de haut)
    snow_color = (240, 248, 255)  # Blanc neige
    pygame.draw.rect(screen, snow_color, (0, 420, width, 60))
    
    # AFFICHAGE DEBUG : Informations à l'écran
    font = pygame.font.Font(None, 24)
    fps_text = font.render(f"FPS: {int(scene.clock.get_fps())}", True, (255, 0, 0))
    time_text = font.render(f"Time: {scene.time_game:.1f}s", True, (255, 0, 0))
    frames_text = font.render(f"Frames: {lib.loops}", True, (255, 0, 0))
    
    screen.blit(fps_text, (10, 10))
    screen.blit(time_text, (10, 35))
    screen.blit(frames_text, (10, 60))
    
    return True  # Continue le jeu


def game_init(scene: lib.Scene) -> List:
    """
    Fonction d'initialisation appelée au démarrage.
    Pour l'instant, ne crée pas d'objets.
    """
    width = scene.window_size[0]
    height = scene.window_size[1]
    
    print("=== INITIALISATION DU JEU ===")
    print(f"Résolution : {width}×{height}")
    print(f"FPS cible : {scene.tick}")
    print("Appuyez sur ECHAP pour quitter")
    print("============================")
    
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

