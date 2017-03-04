from random import randint, choice

import pygame as pg

from .. import prepare
from ..tools import strip_from_sheet
from ..components.monsters import Monster



sheet = prepare.GFX["sheet"]
TILES = {
        "floor": strip_from_sheet(sheet, (736, 512), (32, 32), 4),
        "wall": strip_from_sheet(sheet, (128, 576), (32, 32), 4),
        "door-n": strip_from_sheet(sheet, (736, 352), (32, 32), 1)[0],
        "door-n-open": strip_from_sheet(sheet, (864, 352), (32, 32), 1)[0],
        "stairs-down": strip_from_sheet(sheet, (1312, 480), (32, 32), 1)[0],
        "stairs-up": strip_from_sheet(sheet, (1344, 480), (32, 32), 1)[0],
        "chest-closed": strip_from_sheet(sheet, (1408, 1440), (32, 32), 1)[0],
        "chest-open": strip_from_sheet(sheet, (1440, 1440), (32, 32), 1)[0]
        }

for d, angle in zip(("w", "s", "e"), (90, 180, 270)):
    name = "door-{}".format(d)
    img = pg.transform.rotate(TILES["door-n"], angle)
    TILES[name] = img
    open_name = "door-{}-open".format(d)
    TILES[open_name] = pg.transform.rotate(TILES["door-n-open"], angle)


class Staircase(pg.sprite.Sprite):
    def __init__(self, cell_index, direction, level, *groups):
        super(Staircase, self).__init__(*groups)
        self.cell_index = cell_index
        cell = level.level_grid.cells[cell_index]
        self.direction = direction
        d = "down" if direction == 1 else "up"
        self.image = TILES["stairs-{}".format(d)]
        self.rect = self.image.get_rect(topleft=cell.rect.topleft)
        cell.occupant = self

    def interact(self, dungeon):
        try:
            new_level = dungeon.levels[dungeon.current_level.level_num + self.direction]
        except KeyError:
            return
        dungeon.current_level.level_grid.cells[dungeon.player.cell_index].occupant = None
        dungeon.current_level = new_level
        if self.direction == 1:
            indx = new_level.entrance_index[0] + self.direction, new_level.entrance_index[1]
        else:
            indx = new_level.exit_index[0] + self.direction, new_level.exit_index[1]
        cell = new_level.level_grid.cells[(indx[0], indx[1])]
        new_level.topleft = [-(cell.rect.left - (prepare.SCREEN_SIZE[0]//2)),
                                     -(cell.rect.top - (prepare.SCREEN_SIZE[1]//2))]
        cell.occupant = dungeon.player
        dungeon.player.cell_index = cell.cell_index
        dungeon.player.rect = cell.rect.copy()


class Door(pg.sprite.Sprite):
    def __init__(self, cell, direction, room_num, *groups):
        super(Door, self).__init__(*groups)
        self.room_num = room_num
        self.cell = cell
        self.cell_index = self.cell.cell_index
        self.cell.terrain = "door"
        self.closed_image = TILES["door-{}".format(direction)]
        self.open_image = TILES["door-{}-open".format(direction)]
        self.image = self.closed_image
        self.rect = self.cell.rect.copy()
        self.locked = False


    def open(self, dungeon):
        if not self.locked:
            level = dungeon.current_level
            room = level.rooms[self.room_num]
            x, y = self.rect.left - room.rect.left, self.rect.top - room.rect.top
            room.image.blit(choice(TILES["floor"]), (x, y))
            self.cell.terrain = "floor"
            self.cell.occupant = None
            room.discovered = True
            for hallway in level.hallways:
                if self in hallway.doors:
                    hallway.discovered = True
            self.image = self.open_image


class Room(object):
    def __init__(self, room_num, dimensions, center_index, cell_size, level_grid):
        self.room_num = room_num
        self.center_index = center_index
        self.cells_wide = dimensions[0]
        self.cells_high =  dimensions[1]
        cx, cy = center_index
        w, h = self.cells_wide, self.cells_high
        left = cx - (w//2)
        top = cy - (h//2)
        self.topleft_index = (left, top)
        self.rect = pg.Rect(left*cell_size, top*cell_size,
                                    self.cells_wide*cell_size, self.cells_high*cell_size)
        self.door_indices = {
                "n": (cx, top),
                "s": (cx, top + (self.cells_high - 1)),
                "e": (left + (self.cells_wide - 1), cy),
                "w": (left, cy)}
        self.floor_cells = []
        self.wall_cells = []
        self.door_directions = []
        self.doors = pg.sprite.Group()
        grid_cells = level_grid.cells
        for x in range(1, self.cells_wide-1):
            for y in range(1, self.cells_high-1):
                cell = grid_cells[(left + x, top + y)]
                cell.terrain = "floor"
                self.floor_cells.append(cell)
        for x in range(self.cells_wide):
            cell = grid_cells[(left + x, top)]
            cell.terrain = "wall"
            self.wall_cells.append(cell)
            cell = grid_cells[(left + x, top + self.cells_high-1)]
            cell.terrain = "wall"
            self.wall_cells.append(cell)
        for y in range(1, self.cells_high-1):
            cell = grid_cells[(left, top + y)]
            cell.terrain = "wall"
            self.wall_cells.append(cell)
            cell = grid_cells[(left + self.cells_wide-1, top + y)]
            cell.terrain = "wall"
            self.wall_cells.append(cell)
        self.discovered = False
        self.items = pg.sprite.Group()

    def make_image(self):
        surf  = pg.Surface(self.rect.size)
        for f in self.floor_cells:
            surf.blit(choice(TILES["floor"]), f.rect.move(-self.rect.left, -self.rect.top))
        for w in self.wall_cells:
            surf.blit(choice(TILES["wall"]), w.rect.move(-self.rect.left, -self.rect.top))
        self.image = surf

    def get_open_cell(self):
        open_cells = [x for x in self.floor_cells if x.occupant is None]
        if open_cells:
            return choice(open_cells)

    def add_monster(self, monster_name, level):
        cell = self.get_open_cell()
        if cell:
            monster = Monster(monster_name, cell.cell_index, self, level, level.monsters)
            cell.occupant = monster
            return True
        return False




class Hallway(object):
    def __init__(self, path_cells, level_grid):
        self.path_cells = path_cells
        self.discovered = False
        self.doors = pg.sprite.Group()

    def add_floors(self, level_grid):
        new_floors = set((x for x in self.path_cells))
        wall_cells = set()
        for cell in self.path_cells:
            if cell.terrain == "empty":
                cell.terrain = "floor"
            elif cell.terrain == "door":
                self.doors.add(cell.occupant)
            neighbors = level_grid.get_neighbors(cell.cell_index)
            for n in neighbors:
                if n.terrain in ("empty", "floor"):
                    new_floors.add(n)
                    n.terrain = "floor"
                elif n.terrain == "wall":
                    wall_cells.add(n)
        self.floor_cells = list(new_floors)
        self.wall_cells = wall_cells

    def add_walls(self, level_grid):
        for floor in self.floor_cells:
            neighboring = level_grid.get_neighbors(floor.cell_index, "vonNeuman", 1)
            for neighbor in neighboring:
                if neighbor.terrain in ("empty", "wall"):
                    neighbor.terrain = "wall"
                    self.wall_cells.add(neighbor)

    def make_image(self):
        left = min([x.rect.left for x in self.wall_cells])
        right = max([x.rect.right for x in self.wall_cells])
        top = min([x.rect.top for x in self.wall_cells])
        bottom = max([x.rect.bottom for x in self.wall_cells])
        self.rect = pg.Rect(left, top, right-left, bottom-top)
        self.image = pg.Surface(self.rect.size).convert_alpha()
        self.image.fill((0,0,0,0))
        for cell in self.floor_cells:
            self.image.blit(choice(TILES["floor"]), cell.rect.move(-self.rect.left, -self.rect.top))
        for wall in self.wall_cells:
            self.image.blit(choice(TILES["wall"]), wall.rect.move(-self.rect.left, -self.rect.top))


