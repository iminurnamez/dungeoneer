import pygame as pg

from .. import prepare
from ..tools import strip_from_sheet
from ..components.labels import Label


class DungeonUI(object):
    def __init__(self, dungeon):
        left = prepare.SCREEN_RECT.right - 48
        style = {"font_size": 24, "text_color": "gray80"}
        self.labels = pg.sprite.Group()
        self.attack_label = Label("0", {"topleft": (left, 8)}, self.labels, **style)
        self.defense_label = Label("0", {"topleft": (left, 56)}, self.labels, **style)
        self.update_labels(dungeon)
        sheet = prepare.GFX["sheet"]
        self.sword = strip_from_sheet(sheet, (1312, 1504), (32, 32), 1)[0]
        self.shield = strip_from_sheet(sheet, (1408, 1408), (32, 32), 1)[0]
        left = prepare.SCREEN_RECT.right - 96
        self.sword_rect = self.sword.get_rect(topleft=(left, 8))
        self.shield_rect = self.shield.get_rect(topleft=(left, 56))
        self.health_bar = HealthBar()

    def update_labels(self, dungeon):
        player = dungeon.player
        att = player.strength
        if player.items["Melee Weapon"]:
            att += player.items["Melee Weapon"].stats["Attack"]
        if "{}".format(att) != self.attack_label.text:
            self.attack_label.set_text("{}".format(att))
        defense = player.reflexes
        if player.items["Armor"]:
            defense += player.items["Armor"].stats["Defense"]
        if "{}".format(defense) != self.defense_label.text:
            self.defense_label.set_text("{}".format(defense))

    def update(self, dungeon):
        self.update_labels(dungeon)
        self.health_bar.update(dungeon)

    def draw(self, surface):
        surface.blit(self.sword, self.sword_rect)
        surface.blit(self.shield, self.shield_rect)
        self.labels.draw(surface)
        self.health_bar.draw(surface)


class HealthBar(object):
    def __init__(self):
        self.rect = pg.Rect(8, 8, 160, 16)
        self.fill_color = "gray30"
        self.frame_color = "gray40"
        self.bar_color = (0, 128, 64)

    def update(self, dungeon):
        player = dungeon.player
        val = player.health / float(player.max_health)
        w = int(val * self.rect.w)
        self.bar = pg.Rect(self.rect.topleft, (w, self.rect.h))

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color(self.fill_color), self.rect)
        pg.draw.rect(surface, pg.Color(*self.bar_color), self.bar)
        pg.draw.rect(surface, pg.Color(self.frame_color), self.rect, 2)

