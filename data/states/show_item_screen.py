from random import randint

import pygame as pg

from .. import tools, prepare
from ..components.labels import Label


class ShowItemScreen(tools._State):
    def __init__(self):
        super(ShowItemScreen, self).__init__()

    def startup(self, persistent):
        self.persist = persistent
        self.dungeon = self.persist["dungeon"]
        icon = self.dungeon.args[0]
        item = icon.item
        self.rect = pg.Rect(0, 0, 480, 480)
        self.image = pg.Surface(self.rect.size)
        self.image.fill(pg.Color("gray30"))
        self.image.fill(pg.Color("gray20"), self.rect.inflate(-4, -4))

        self.labels = pg.sprite.Group()
        text = "You found a {}!".format(item.item_type)
        Label(text, {"midtop": (self.rect.centerx, self.rect.top + 10)},
                self.labels, font_size=32, text_color="gray70")
        r = icon.rect.copy()
        r.center = self.rect.centerx, 100
        self.image.blit(icon.image, r)
        Label(item.name, {"midtop": (self.rect.centerx, 150)},
                self.labels, font_size=32, text_color="gray70")
        top = 200
        for stat in item.stats:
            Label("{}   {}".format(stat, item.stats[stat]),
                    {"midtop": (self.rect.centerx, top)},
                    self.labels, font_size=24, text_color="gray70")
            top += 30
        Label("Press E to equip", {"midbottom": (self.rect.centerx, self.rect.bottom - 32)},
                self.labels, font_size=18, text_color="gray65")
        Label("Press Enter to continue",
                {"midbottom": (self.rect.centerx, self.rect.bottom-8)},
                self.labels, font_size=16, text_color="gray65")
        self.labels.draw(self.image)
        self.rect.center = prepare.SCREEN_RECT.center
        self.item = item
        self.dungeon.current_level.level_grid.cells[icon.cell_index].occupant = None
        icon.kill()

    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_e:
                self.dungeon.player.equip(self.item)
                self.done = True
                self.next = "GAMEPLAY"
            elif event.key == pg.K_RETURN:
                self.done = True
                self.next = "GAMEPLAY"

    def update(self, dt):
        mouse_pos = pg.mouse.get_pos()


    def draw(self, surface):
        surface.blit(self.image, self.rect)



