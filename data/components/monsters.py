from random import randint

import pygame as pg

from ..tools import strip_from_sheet as strip
from .. import prepare


image_info = {
    "Snake": [(1088, 128), (32, 32)],
    "Gargoyle": [(1024, 192), (32, 32)]
    }

IMAGES = {}
for name in image_info:
    spot, size = image_info[name]
    IMAGES[name] = strip(prepare.GFX["sheet"], spot, size, 1)[0]


class Monster(pg.sprite.Sprite):
    def __init__(self, name, cell_index, room, level, *groups):
        super(Monster, self).__init__(*groups)
        self.image = IMAGES[name]
        self.cell_index = cell_index
        self.rect = level.level_grid.cells[cell_index].rect
        self.room = room
        self.state = "Idle"
        self.speed = 2
        self.range = 1
        self.attack_bonus = 5
        self.damage = (1, 3)
        self.defense = 8
        self.health = 5

    def move_to(self, cell, level):
        old_cell = level.level_grid.cells[self.cell_index]
        old_cell.occupant = None
        self.cell_index = cell.cell_index
        cell.occupant = self
        self.rect = cell.rect.copy()

    def attack(self, player):
        attack = randint(1, 21) + self.attack_bonus
        if attack > player.defense:
            damage = randint(*self.damage)
            player.health -= damage

    def die(self, level):
        level.level_grid.cells[self.cell_index].occupant = None
        self.kill()

    def update(self, level, player):
        if self.health <= 0:
            self.die(level)
            return
        moves_left = self.speed

        if level.level_grid.cells[player.cell_index] in self.room.floor_cells:
            self.state = "Attacking"
        if self.state == "Attacking":
            neighbors = level.level_grid.get_neighbors(self.cell_index)
            floors = [x for x in neighbors if x.terrain == "floor"]
            open = [x for x in floors if x.occupant is None]
            for n in neighbors:
                if n.occupant == player:
                    self.attack(player)
                    break
            else:
                path = level.level_grid.find_path(self.cell_index, player.cell_index, ["floor"], "Moore")
                if path:
                    self.move_to(path[1], level)
