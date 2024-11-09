from typing import Any
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class Pathfinder:
    def __init__(self, map: Any):
        self.grid = self.convertMapToGrid(map)
        self.finder = AStarFinder()
    
    def find_path(self, start: tuple, end: tuple) -> list[tuple[int, int]]:
        start = self.grid.node(start[0], start[1])
        end = self.grid.node(end[0], end[1])
        # print(f'start {start} -> end {end}')
        path, runs = self.finder.find_path(start, end, self.grid)
        path = [(n.x, n.y) for n in path]
        return path
        

    def convertMapToGrid(self, map: Any) -> Grid:
        new_map = []
        for row in map.getMapArray():
            new_row = []
            for col in row:
                if col in [2, 3]:
                    col = 1
                new_row.append(col)
            new_map.append(new_row)

        return Grid(matrix=new_map)
