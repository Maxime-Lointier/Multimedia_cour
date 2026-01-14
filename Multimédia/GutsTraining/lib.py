#librairie principale du jeu

from collections.abc import Callable
from typing import List, Optional
from xml.etree.ElementTree import Element

import pygame


class Scene:
    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        init: Optional[Callable[["Scene"], List[Element]]] = None,
        controller: Optional[
            Callable[[List[Element], pygame.event.Event], bool]
        ] = None,
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
        self.objects: List[Element] = []
        if init is not None:
            self.objects = init(self)
        self.prepaint = prepaint
        self.objects_by_depth = sorted(self.objects, key=lambda x: x.depth)
        self.objects.sort(key=lambda x: x.id)
        self.controller = controller

    def mainloop(self) -> bool:
            pass