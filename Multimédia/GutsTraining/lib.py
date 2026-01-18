from collections.abc import Callable
from typing import List, Optional
import pygame

loops = 0


class Scene:
    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        init: Optional[Callable[["Scene"], List]] = None,
        controller: Optional[Callable[[List, pygame.event.Event], bool]] = None,
        prepaint: Optional[Callable[["Scene"], bool]] = None,
        tick=60,
    ) -> None:
        pygame.init()
        pygame.mixer.init()
        
        self.clock = pygame.time.Clock()
        self.tick = tick
        self.time_game: float = 0.0
        
        self.window_size = width, height
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Guts Training - Dithering Demo")
        
        self.objects: List = []
        self.static_background = None
        self.middle_ground = None
        self.snow_ground = None
        self.tree = None
        
        if init is not None:
            self.objects = init(self)
        
        self.prepaint = prepaint
        self.controller = controller

    def mainloop(self) -> bool:
        global loops
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            
            if self.controller:
                if not self.controller(self.objects, event):
                    return False
        
        self.screen.fill((0, 0, 0))
        
        if self.prepaint:
            if not self.prepaint(self):
                return False
        
        pygame.display.flip()
        
        elapsed = self.clock.tick(self.tick)
        self.time_game += elapsed / 1000.0
        loops += 1
        
        return True

SKY_COLORS = [
    (200, 210, 220),
    (175, 185, 200),
    (150, 165, 185),
    (125, 140, 165),
    (100, 115, 145),
    (80, 95, 125),
]

SUN_COLORS = [
    (255, 250, 200),
    (255, 230, 120),
    (255, 200, 80),
    (240, 160, 60),
]

HILL_COLORS = [
    (160, 170, 175),
    (135, 145, 155),
    (115, 125, 140),
]

GROUND_COLORS = [
    (180, 140, 100),
    (150, 110, 80),
    (120, 80, 60),
    (90, 60, 45),
    (60, 40, 30),
]

GRASS_COLORS = [
    (100, 110, 85),
    (80, 90, 70),
    (60, 70, 55),
    (45, 55, 45),
]

TREE_COLORS = [
    (20, 15, 10),
    (30, 20, 15),
    (40, 28, 20),
    (50, 35, 25),
    (60, 42, 28),
    (70, 48, 32),
    (80, 55, 38),
    (90, 62, 42),
    (100, 70, 48),
    (110, 78, 55),
]

SNOW_COLORS = [
    (255, 255, 255),
    (230, 235, 245),
    (200, 210, 220),
]

GUTS_COLORS = [
    (50, 52, 58),
    (35, 37, 42),
    (70, 72, 78),
    (25, 27, 30),
    (180, 140, 120),
    (140, 100, 85),
    (30, 30, 32),
    (15, 15, 18),
    (90, 92, 95),
    (120, 122, 128),
]

FULL_PALETTE = (
    SKY_COLORS + 
    SUN_COLORS + 
    HILL_COLORS +
    GROUND_COLORS +
    GRASS_COLORS +
    TREE_COLORS + 
    SNOW_COLORS + 
    GUTS_COLORS
)

print(f"Nombre total de couleurs : {len(FULL_PALETTE)}")

BAYER_MATRIX_4x4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]

def color_distance(c1, c2):
    r1, g1, b1 = c1
    r2, g2, b2 = c2
    return ((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2) ** 0.5


def find_closest_colors(target_color, palette):
    distances = [(color_distance(target_color, c), c) for c in palette]
    
    distances.sort(key=lambda x: x[0])
    
    closest_color = distances[0][1]
    second_closest_color = distances[1][1]
    
    dist1 = distances[0][0]
    dist2 = distances[1][0]
    
    if dist1 + dist2 == 0:
        ratio = 1.0
    else:
        ratio = dist2 / (dist1 + dist2)
    
    return closest_color, second_closest_color, ratio


def dither_pixel(x, y, target_color, palette):
    color1, color2, ratio = find_closest_colors(target_color, palette)
    
    bayer_x = x % 4
    bayer_y = y % 4
    threshold = BAYER_MATRIX_4x4[bayer_y][bayer_x] / 16.0
    
    if ratio > threshold:
        return color1
    else:
        return color2


def dither_gradient(x, y, color_start, color_end, gradient_start, gradient_end, palette):
    if gradient_end - gradient_start == 0:
        t = 0.0
    else:
        t = (y - gradient_start) / (gradient_end - gradient_start)
        t = max(0.0, min(1.0, t))
    
    r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
    g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
    b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
    
    target_color = (r, g, b)
    
    return dither_pixel(x, y, target_color, palette)