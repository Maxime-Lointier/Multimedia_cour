import pygame
import traceback
from typing import List
import lib


def game_init(scene: lib.Scene) -> List[lib.Element]:
    width = scene.window_size[0]
    height = scene.window_size[1]
    objects = []
    return objects


game = lib.Scene(init=game_init)
# If needed, wait before starting
# game.startupdelay(5)
RUN = True
while RUN:
    RUN = game.mainloop() ## censer être la logique du jeu, la boucle principale gameplay
print(f"Window closed after {lib.loops} frames")

################## MINE #####################
def load_game(context, time_game, elapsed_time, loops):
    load_backgrounds(context.screen)
    load_gameplay()
    load_snow()

def load_backgrounds(screen):
    screen.fill((255,255,255))
    sol = pygame.Rect(0,screen.get_height(),screen.get_width(),50)
    pygame.draw.rect(screen,(0,0,0), sol)
    pass

def load_gameplay():
    load_player()
    load_wood()
    load_ath()

def load_player():
    pass

def load_wood():
    pass

def load_ath():
    pass

def load_snow():
    pass

