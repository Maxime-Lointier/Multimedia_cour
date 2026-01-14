import libgame
import pygame
from typing import List, Tuple, Dict, Optional, Callable


def game_init(scene: libgame.Scene) -> List[libgame.Element]:
    width = scene.window_size[0]
    height = scene.window_size[1]
    objects = [
        libgame.AutoWalker(width // 8, height // 4, vx=0),
        libgame.Ground((255, 0, 0), 0, height - 20, width, 20),
        libgame.Ground((255, 0, 0), width, height - 50, width, 50),
        libgame.Tree(100, height - 20, 8),
        libgame.Tree(150, height - 20, 9),
        libgame.Tree(125, height - 20, 5),
    ]
    return objects


def game_test(objects: List[libgame.Element], event: pygame.event.Event):
    if event.type == pygame.KEYDOWN:
        for obj in objects:
            res = obj.do_event(event)
            if not res:
                return False
    return True


def game_prepaint(scene: libgame.Scene) -> bool:
    walker = scene.objects[0]
    dx = walker.rect.centerx - scene.window_size[0] // 2
    if abs(dx) > 0:
        for obj in scene.objects:
            obj.x -= dx * obj.depth / 10
            obj.adjust_position_from_center()
    if walker.rect.top > scene.window_size[1] * 2:
        return False
    return True


if __name__ == "__main__":
    game = libgame.Scene(init=game_init, controller=game_test, prepaint=game_prepaint)
    # If needed, wait before starting
    # game.startupdelay(5)
    RUN = True
    while RUN:
        RUN = game.mainloop()
    print(f"Window closed after {libgame.loops} frames")
