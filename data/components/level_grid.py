import pygame as pg


class GridCell(object):
    def __init__(self, cell_index, cell_size, terrain=None):
        self.cell_index = cell_index
        self.terrain = "empty" if terrain is None else terrain
        self.occupant = None
        self.rect = pg.Rect(cell_index[0] * cell_size, cell_index[1] * cell_size,
                                    cell_size, cell_size)


class LevelGrid(object):
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, width, height, cell_size):
        self.cells = {(x, y): GridCell((x, y), cell_size)
                          for x in range(width)
                          for y in range(width)}
        self.rooms = []
        self.rect = pg.Rect(0, 0, width * cell_size, height * cell_size)
        self.center_index = (width//2, height//2)
        self.empty_color = (30, 17, 40)

    def get_neighbors(self, cell_index, neighborhood="Moore", depth=1):
        x, y = cell_index
        neighbors = []
        if neighborhood == "vonNeuman":
            offsets = [(1, -1), (1, 0), (1, 1), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1)]
        else:
            offsets = self.offsets
        for off in offsets:
            try:
                nx, ny = x + off[0], y + off[1]
                n = self.cells[(nx, ny)]
                neighbors.append(n)
            except KeyError:
                pass
        return neighbors

    def find_path_to(self, origin, destination, valid_terrains, neighborhood="Moore", depth=1):
        origin = self.cells[origin]
        destination = self.cells[destination]
        visited = set()
        levels = [[(origin, origin)]]
        while True:
            neighbors = []
            for cell, parent in levels[-1]:
                candidates = self.get_neighbors(cell.cell_index, neighborhood, depth)
                for c in candidates:
                    if c == destination:
                        levels.append([(c, cell)])
                        return levels
                    if c not in visited and c.terrain in valid_terrains:
                        neighbors.append((c, cell))
                    visited.add(c)
            if neighbors:
                levels.append(neighbors)
            else:
                return None

    def backtrack(self, path_cells):
        dest = path_cells[-1][0][0]
        route =[dest]
        for level in path_cells[::-1]:
            for cell, parent in level:
                if parent == path_cells[0][0][0]:
                    route.append(parent)
                    return route[::-1]
                if cell == route[-1]:
                    route.append(parent)
                    break

    def find_path(self, origin, destination, valid_terrains, neighborhood="Moore", depth=1):
        to = self.find_path_to(origin, destination, valid_terrains, neighborhood, depth)
        if to:
            return self.backtrack(to)




