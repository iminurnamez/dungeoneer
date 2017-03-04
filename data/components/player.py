from random import choice, randint

import pygame as pg

from .. import prepare
from ..tools import strip_from_sheet


sheet = prepare.GFX["sheet"]
PLAYER_TILES = {
    "human-female": strip_from_sheet(sheet, (0, 992), (32, 32), 1)[0],
    "human-male": strip_from_sheet(sheet, (32, 992), (32, 32), 1)[0]
    }


class Player(pg.sprite.Sprite):
    def __init__(self, cell, *groups):
        super(Player, self).__init__(*groups)
        self.cell_index = cell.cell_index
        self.speed = 1
        self.strength = 1
        self.reflexes = 1
        self.health = self.max_health = 10
        self.defense = 1
        self.items = {
                "Armor": None,
                "Melee Weapon": None}

        self.move_keys = {
                pg.K_LEFT: (-1, 0),
                pg.K_RIGHT: (1, 0),
                pg.K_UP: (0, -1),
                pg.K_DOWN: (0, 1)}
        self.state = "Idle"
        self.gender = choice(("male", "female"))
        self.base_image = PLAYER_TILES["human-{}".format(self.gender)]
        self.rect = cell.rect.copy()
        self.make_image()
        self.acted = False
        self.key_timer = 0
        self.key_cooldown = 100

    def make_image(self):
        self.image = self.base_image.copy()
        armor = self.items["Armor"]
        weapon = self.items["Melee Weapon"]
        if armor:
            armor.draw(self.image)
        if weapon:
            weapon.draw(self.image)

    def move_to(self, cell, dungeon):
        level = dungeon.current_level
        cells = level.level_grid.cells
        old_cell = cells[self.cell_index]
        old_cell.occupant = None
        self.cell_index = cell.cell_index
        cell.occupant = self
        self.rect = cell.rect.copy()
        level.topleft[0] -= cell.rect.left - old_cell.rect.left
        level.topleft[1] -= cell.rect.top - old_cell.rect.top
        self.acted = True

    def equip(self, item):
        self.items[item.item_type] = item
        self.make_image()

    def attack(self, monster):
        attack_score = randint(1, 21) + self.strength
        weapon = self.items["Melee Weapon"]
        if weapon:
            attack_score += weapon.stats["Attack"]
        if attack_score > monster.defense:
            damage = self.strength
            if weapon:
                damage += randint(*weapon.stats["Damage"])
            monster.health -= damage
        self.acted = True

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        self.acted = True
        self.key_timer += self.key_cooldown

    def update(self, dt, dungeon):
        if self.health < 0:
            self.health = 0
        if self.acted:
            return
        keys = pg.key.get_pressed()
        if keys[pg.K_h] and not self.key_timer:
            self.heal(1)
            self.key_timer += self.key_cooldown
            return
        for k in self.move_keys:
            if self.acted:
                break
            if keys[k] and not self.key_timer:
                self.key_timer += self.key_cooldown
                self.act(k, dungeon)
        self.key_timer -= dt
        if self.key_timer < 0:
            self.key_timer = 0

    def act(self, key, dungeon):
        level = dungeon.current_level
        indx = self.move_keys[key]
        x = indx[0] + self.cell_index[0]
        y = indx[1] + self.cell_index[1]
        try:
            neighbor = level.level_grid.cells[(x, y)]
        except KeyError:
            return
        terrain = neighbor.terrain
        occupant = neighbor.occupant
        if terrain == "floor" and occupant in level.monsters:
            self.attack(occupant)
        elif terrain == "floor" and occupant is None:
            self.move_to(neighbor, dungeon)
        elif terrain == "floor" and occupant:
            occupant.interact(dungeon)
        elif terrain == "door" :
            if not occupant.locked:
                occupant.open(dungeon)
                self.move_to(neighbor, dungeon)
