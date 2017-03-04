from random import randint

import pygame as pg

from .. import tools, prepare
from ..components.dungeon import Dungeon


class Gameplay(tools._State):
    def __init__(self):
        super(Gameplay, self).__init__()
        cell_size = 32
        num_levels = 5
        rooms_per_level = (10, 30)
        self.dungeon = Dungeon(num_levels, rooms_per_level, cell_size)

    def startup(self, persistent):
        self.persist = persistent

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True

    def update(self, dt):
        mouse_pos = pg.mouse.get_pos()
        self.dungeon.update(dt, mouse_pos)
        if self.dungeon.done:
            self.next = self.dungeon.next
            self.done = True
            self.dungeon.done = False
            self.persist["dungeon"] = self.dungeon

    def draw(self, surface):
        self.dungeon.draw(surface)


