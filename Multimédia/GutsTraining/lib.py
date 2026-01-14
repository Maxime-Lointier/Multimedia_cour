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