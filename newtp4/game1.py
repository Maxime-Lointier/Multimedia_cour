import libgame
from typing import List, Tuple, Dict, Optional, Callable


def game_init(scene: libgame.Scene) -> List[libgame.Element]:
    width = scene.window_size[0]
    height = scene.window_size[1]
    objects = [
        libgame.Ground((255, 0, 0), 0, height - 20, width, 20),
        libgame.Ground((255, 0, 0), 0, 0, width, 20),
        libgame.Ground((255, 255, 0), 0, 21, 10, height - 42),
        libgame.Ground((255, 255, 0), width - 10, 21, 10, height - 42),
        libgame.Ground((255, 255, 255), width // 2 - 30, height // 2 - 10, 60, 20),
        libgame.Ball(5 * width // 8, 3 * height // 4),
        libgame.Ball(3 * width // 8, height // 4, vx=-100),
        libgame.Ball(1 * width // 8, 3 * height // 4, vx=50),
        libgame.BlueBall(7 * width // 8, height // 4, vx=100),
    ]
    return objects


if __name__ == "__main__":
    game = libgame.Scene(init=game_init)
    # If needed, wait before starting
    # game.startupdelay(5)
    RUN = True
    while RUN:
        RUN = game.mainloop()
    print(f"Window closed after {libgame.loops} frames")
