import pygame as pg

from .. import prepare
from ..tools import strip_from_sheet


image_coords = {
    "Club": (0, 1152),
    "Short Sword": (160, 1152),
    "Long Sword": (192, 1152),
    "Chain Mail":(192, 1024),
    "Armor Suit": (192, 1056),
    "Spike Armor": (96, 1024)}

IMAGES = {}
for name, coord in image_coords.items():
    img = strip_from_sheet(prepare.GFX["sheet"], coord, (32, 32), 1)[0]
    IMAGES[name] = img
icon_coords = {
    "Club": (0, 896),
    "Short Sword": (1024, 896),
    "Long Sword": (640, 896),
    "Chain Mail": (1056, 672),
    "Armor Suit": (992, 672),
    "Spike Armor": (1312, 672)}
ICONS = {}
for name, coord in icon_coords.items():
    img = strip_from_sheet(prepare.GFX["sheet"], coord, (32, 32), 1)[0]
    ICONS[name] = img

STAT_NAMES = {
    "Melee Weapon": ["Attack", "Damage"],
    "Armor": ["Defense"]
    }
ITEM_STATS = {
    "Melee Weapon": {
        "Club": [5, (1, 4)],
        "Short Sword": [10, (2, 13)],
        "Long Sword": [10, (3, 25)]},
    "Armor": {
        "Chain Mail": [5],
        "Armor Suit": [10],
        "Spike Armor": [15]}
    }
LEVEL_ITEMS = {
    1: [("Melee Weapon", "Club"), ("Armor", "Chain Mail")],
    2: [("Melee Weapon", "Short Sword")],
    3: [("Armor", "Armor Suit")],
    4: [("Melee Weapon", "Long Sword"), ("Armor", "Spike Armor")],
    5: []
    }


class ItemIcon(pg.sprite.Sprite):
    def __init__(self, item_type, item_name, cell, *groups):
        super(ItemIcon, self).__init__(*groups)
        self.cell = cell
        self.cell_index = cell.cell_index
        self.image = ICONS[item_name]
        self.rect = cell.rect.copy()
        self.item = PlayerItem(item_type, item_name)

    def interact(self, dungeon):
        dungeon.show_item(self)


class PlayerItem(object):
    def __init__(self, item_type, item_name):
        self.item_type = item_type
        self.name = item_name
        self.image = IMAGES[item_name]
        self.rect = self.image.get_rect()
        self.stats = {k: v for k, v in zip(STAT_NAMES[item_type],
                           ITEM_STATS[item_type][item_name])}

    def draw(self, surface):
        surface.blit(self.image, self.rect)