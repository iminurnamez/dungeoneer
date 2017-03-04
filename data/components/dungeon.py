from math import sqrt
from random import shuffle, choice, randint

import pygame as pg

from .. import prepare
from ..tools import strip_from_sheet
from ..components.labels import Label
from ..components.level_grid import LevelGrid
from ..components.dungeon_entities import Door, Staircase, Room, Hallway
from ..components.monsters import IMAGES as monster_images
from ..components.player import Player
from ..components.player_items import ItemIcon, LEVEL_ITEMS
from ..components.dungeon_ui import DungeonUI


OFFSETS = {
        "n": (0, -1),
        "s": (0, 1),
        "e": (1, 0),
        "w": (-1, 0)}


class Dungeon(object):
    def __init__(self, num_levels, num_rooms_per_floor, cell_size):
        self.levels = {}
        for x in range(num_levels):
            level_num = x + 1
            num_rooms = randint(*num_rooms_per_floor)
            while True:
                try:
                    level = DungeonLevel(level_num, num_rooms, cell_size)
                    break
                except Exception as e:
                    pass
            self.levels[level_num] = level
        self.current_level = self.levels[1]
        indx = (self.current_level.entrance_index[0] + 1,
                   self.current_level.entrance_index[1])
        cell = self.current_level.level_grid.cells[(indx[0], indx[1])]
        self.player = Player(cell)
        self.done = False
        self.next = None
        self.ui = DungeonUI(self)

    def update(self, dt, mouse_pos):
        self.player.update(dt, self)
        self.current_level.update(dt, mouse_pos, self.player)
        self.ui.update(self)

    def show_item(self, item_name):
        self.done = True
        self.next = "SHOW_ITEM"
        self.args = [item_name]

    def draw(self, surface):
        self.current_level.draw(surface, self.player)
        self.ui.draw(surface)


class DungeonLevel(object):
    connection_distance_range = (3, 16)
    room_size_range = (7, 23)
    opposites = {
            "n": "s",
            "s": "n",
            "e": "w",
            "w": "e",
            "top": "bottom",
            "bottom": "top",
            "left": "right",
            "right": "left",
            "-inner": "-outer",
            "-outer": "-inner"}
    grid_size = 600
    scroll_speed = 4
    def __init__(self, level_num, num_rooms, cell_size):
        self.topleft = [
                -(cell_size * (self.grid_size//2)) + (prepare.SCREEN_SIZE[0]//2),
                -(cell_size * (self.grid_size//2)) + (prepare.SCREEN_SIZE[1]//2)]
        self.num_rooms = num_rooms
        num_branches = randint(1, int(sqrt(num_rooms)) + 1)
        self.level_num = level_num
        self.level_grid = LevelGrid(self.grid_size, self.grid_size, cell_size)
        apportioned = self.apportion_branches(num_rooms, num_branches)
        numbered = self.number_rooms(apportioned)
        entrance_num = numbered[0][0]
        exit_num = numbered[0][-1]
        splits = self.pick_split_spots(numbered)
        connections = self.make_connections(numbered, splits)
        room_map = self.make_room_map(numbered)
        self.make_rooms(connections, room_map, cell_size)
        self.entrance_index = self.rooms[entrance_num].center_index
        self.exit_index = self.rooms[exit_num].center_index
        self.staircases = pg.sprite.Group()
        Staircase(self.entrance_index, -1, self, self.staircases)
        Staircase(self.exit_index, 1, self, self.staircases)

        self.monsters = pg.sprite.Group()
        self.add_monsters()
        self.add_items()

    def add_monsters(self):
        num_encounters = randint(self.level_num * 2, self.level_num * 4)
        while num_encounters:
            room_num = choice(list(self.rooms.keys()))
            monster = choice(list(monster_images.keys()))
            self.rooms[room_num].add_monster(monster, self)
            num_encounters -= 1

    def add_items(self):
        items = LEVEL_ITEMS[self.level_num]
        for item_type, name in items:
            while True:
                room = choice(list(self.rooms.values()))
                cell = room.get_open_cell()
                if cell:
                    item = ItemIcon(item_type, name, cell, room.items)
                    cell.occupant = item
                    break

    def update(self, dt, mouse_pos, player):
        if player.acted:
            self.monsters.update(self, player)
        player.acted = False

    def get_random_room_size(self):
        w = randint(*self.room_size_range)
        h = randint(*self.room_size_range)
        return w, h

    def apportion_branches(self, num_rooms, num_branches):
        if num_branches == 1:
            return [num_rooms]
        rooms_left = num_rooms
        branches_left = num_branches
        branches = []
        for _ in range(num_branches):
            num = randint(1, (rooms_left-branches_left)+1)
            branches.append(num)
            rooms_left -= num
            branches_left -= 1
        return sorted(branches, reverse=True)

    def number_rooms(self, branches):
        total = sum(branches)
        branch_rooms = []
        current = 0
        for b in branches:
            branch = []
            for x in range(b):
                branch.append(current)
                current += 1
            branch_rooms.append(branch)
        return branch_rooms

    def pick_split_spots(self, branch_rooms):
        num_splits = len(branch_rooms) - 1
        valid = branch_rooms[0][:-1]
        split_spots = []
        for i, branch in enumerate(branch_rooms):
            if num_splits:
                while True:
                    spot = choice(valid)
                    if split_spots.count(spot) < 2:
                        split_spots.append((spot, i + 1))
                        num_splits -= 1
                        break
        return split_spots

    def make_connections(self, branch_rooms, split_spots):
        connections = []
        for branch in branch_rooms:
            for i, room_num in enumerate(branch, start=1):
                try:
                    connections.append((room_num, branch[i]))
                except IndexError:
                    pass
                for split_num, branch_num in split_spots:
                    if room_num == split_num:
                        connections.append((room_num, branch_rooms[branch_num][0]))
        return connections

    def make_room_map(self, branch_rooms):
        room_map = {}
        for b in branch_rooms:
            for n in b:
                room_map[n] = [self.get_random_room_size(), ["e", "w", "n", "s"]]
        return room_map

    def make_rooms(self, connections, room_map, cell_size):
        start_index = self.level_grid.center_index
        rooms = {0: Room(0, room_map[0][0], start_index, cell_size, self.level_grid)}
        rooms[0].discovered = True
        paths = []
        for connection in connections:
            self.add_room(connection, rooms, paths, room_map, cell_size)
        self.hallways = []
        for path in paths:
            hallway = Hallway(path, self.level_grid)
            self.hallways.append(hallway)
        for hall in self.hallways:
            hall.add_floors(self.level_grid)
        for h in self.hallways:
            h.add_walls(self.level_grid)
        self.rooms = rooms

        for room in self.rooms.values():
            room.make_image()
        for hallway in self.hallways:
            hallway.make_image()

    def add_room(self, connection, rooms, paths, room_map, cell_size):
        origin_num, dest_num = connection
        try:
            origin = rooms[origin_num]
        except KeyError:
            pass
        room_rects = [room.rect for room in rooms.values()]
        room_rects.extend([cell.rect for p in paths for cell in p])
        left, top = origin.topleft_index
        bottom = top + origin.cells_high
        right = left + origin.cells_wide
        cw, ch = room_map[connection[1]][0]
        dist = randint(*self.connection_distance_range)
        buffer_w = (cw//2) + 1
        buffer_h = (ch//2) + 1
        spots = {
                "n": (origin.center_index[0],
                        top - (dist + buffer_h)),
                "s": (origin.center_index[0],
                        bottom + (dist + buffer_h)),
                "e": (right + (dist + buffer_w),
                       origin.center_index[1]),
                "w": (left - (dist + buffer_w),
                        origin.center_index[1])}
        new_dimensions = room_map[dest_num][0]
        new_size = [x*cell_size for x in new_dimensions]
        directions = room_map[origin_num][1][:]
        shuffle(directions)
        for direction in directions:
            opposite = self.opposites[direction]
            spot = spots[direction]
            center = [s * cell_size for s in spot]
            new_rect = pg.Rect((0, 0), new_size)
            new_rect.center = center
            for rect in room_rects:
                if rect.colliderect(new_rect):
                    break
            else:
                new_room = Room(dest_num, new_dimensions, spot, cell_size, self.level_grid)
                rooms[dest_num] = new_room
                room_map[origin_num][1].remove(direction)
                room_map[dest_num][1].remove(opposite)
                origin_door = origin.door_indices[direction]
                dest_door = new_room.door_indices[opposite]
                origin.door_directions.append(direction)
                new_room.door_directions.append(opposite)
                o_cell = self.level_grid.cells[origin_door]
                d_cell = self.level_grid.cells[dest_door]
                o_cell.occupant = Door(o_cell, direction, origin_num, origin.doors)
                d_cell.occupant = Door(d_cell, opposite, dest_num, new_room.doors)
                o_cell.terrain = "door"
                d_cell.terrain = "door"
                path = self.level_grid.find_path(origin_door, dest_door, ["empty"], "Moore", 1)
                paths.append(path)
                return

    def make_level_image(self):
        surf = pg.Surface(self.level_grid.rect.size)
        for room in self.rooms.values():
            surf.blit(room.image, room.rect)
        for hallway in self.hallways:
            surf.blit(hallway.image, hallway.rect)
        self.image = surf

    def draw(self, surface, player):
        surface.fill(pg.Color("gray5"))
        doors = []
        for room in self.rooms.values():
            if room.discovered:
                surface.blit(room.image, room.rect.move(self.topleft))
                for item in room.items:
                    surface.blit(item.image, item.rect.move(self.topleft))
                for door in room.doors:
                    doors.append((door.image, door.rect.move(self.topleft)))
        for hallway in self.hallways:
            if hallway.discovered:
                surface.blit(hallway.image, hallway.rect.move(self.topleft))
                for door in hallway.doors:
                    doors.append((door.image, door.rect.move(self.topleft)))
        for stairs in self.staircases:
            surface.blit(stairs.image, stairs.rect.move(self.topleft))
        for monster in self.monsters:
            if monster.room.discovered:
                surface.blit(monster.image, monster.rect.move(self.topleft))
        surface.blit(player.image, player.rect.move(self.topleft))
        for img, rect in doors:
            surface.blit(img, rect)
