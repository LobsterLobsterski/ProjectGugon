
from enum import Enum, IntEnum
from itertools import tee
import random
from typing import Iterable
from pygame.sprite import Group

from sprites import Wall

def pairwise(iterable: Iterable) -> Iterable:
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

class TileType(IntEnum):
    Wall = 0
    Floor = 1
    Player = 2
    Mob = 3

class Room:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return f'Room({self.x}, {self.y}, {self.width}, {self.height})'

    def get_random_tile(self):
        return random.randint(self.x, self.x+self.width-1), random.randint(self.y, self.y+self.height-1)
    
    def set_x(self, x):
        self.x = x
    def set_y(self, y):
        self.y = y
    def set_width(self, width):
        self.width = width
    def set_height(self, height):
        self.height = height

class BinarySpacePartition:
    def _make_room(tile_width: int, tile_height: int, min_splits: int, max_splits: int, debug: bool) -> Room:
        #-1 so they dont spawn in outside walls
        room = Room(1, 1, tile_width-1, tile_height-1)
        NUM_OF_SPLITS = random.randint(min_splits, max_splits)
        is_vertical_split = True
        if debug:
            print('\n', NUM_OF_SPLITS)
        for _ in range(NUM_OF_SPLITS):
            take_second_split = bool(random.getrandbits(1))
            is_vertical_split = not is_vertical_split
            
            if is_vertical_split:
                if take_second_split:
                    room.set_x(room.x+room.width//2)
                room.set_width(room.width//2)
            else:
                if take_second_split:
                    room.set_y(room.y+room.height//2)
                room.set_height(room.height//2)

            if debug:
                print('\ttake second part' if take_second_split else '\ttake first part')
                print('\t\t', room)

        return room
    
    def _add_room_to_map(map: list[list[TileType]], room: Room):
        for row in range(room.y, room.y+room.height):
            for col in range(room.x, room.x+room.width):
                map[row][col] = TileType.Floor
    
    def _create_walls(map: list[list[TileType]], sprite_groups: Iterable[Group]):
        for y, row in enumerate(map):
            for x, tile in enumerate(row):
                if tile == TileType.Wall:
                    Wall(sprite_groups, x, y)
    
    def _make_corridor(map: list[list[TileType]], start: tuple[int, int], finish: tuple[int, int], is_vertical: bool):
        y0, y1 = sorted((start[1], finish[1]))
        x0, x1 = sorted((start[0], finish[0]))

        if is_vertical:
            for y_id in range(y0, y1+1):
                map[y_id][start[0]] = TileType.Floor

            for x_id in range(x0, x1+1):
                map[finish[1]][x_id] = TileType.Floor
        else:
            for x_id in range(x0, x1+1):
                map[finish[1]][x_id] = TileType.Floor

            for y_id in range(y0, y1+1):
                map[y_id][start[0]] = TileType.Floor
    
    def _add_corridors_to_map(map: list[list[TileType]], rooms: Iterable[Room]):
        for room, room2 in pairwise(rooms):
            start, finish = room.get_random_tile(), room2.get_random_tile()
            BinarySpacePartition._make_corridor(map, start, finish, is_vertical=bool(random.getrandbits(1)))
    
    def _encase_map(tile_width: int, tile_height: int, sprite_groups: Iterable[Group]):
        for x in range(tile_width):
            for y in range(tile_height):
                if x in (0, tile_width-2) or y in (0, tile_height-2):
                    Wall(sprite_groups, x, y)
    
    def create_map(tile_width: int, tile_height: int, sprite_groups: Iterable[Group],  debug=False):
        '''
        orderly rooms, dijkstra map to find 
        'essential rooms' and force exploration
        for the sake of progression
        '''
        map = [[TileType.Wall for _ in range(tile_width)] for _ in range(tile_height)]
        rooms = []
        NUM_OF_ROOMS = 10
        for i in range(NUM_OF_ROOMS):
            min_splits, max_splits = (3, 5) if i<2 else (5, 6) if i<7 else (4, 8)
            room = BinarySpacePartition._make_room(tile_width, tile_height, min_splits, max_splits, debug)
            BinarySpacePartition._add_room_to_map(map, room)
            rooms.append(room)

            if debug: print('made room of coords:', room)
        
        BinarySpacePartition._encase_map(tile_width, tile_height, sprite_groups)
        BinarySpacePartition._add_corridors_to_map(map, rooms)
        if debug:
            print('map:')
            for row in map:
                print([int(i) for i in row])
        BinarySpacePartition._create_walls(map, sprite_groups)

        return map, rooms

class CellularAutomata:
    def create_map(tile_width: int, tile_height: int, sprite_groups: Iterable[Group],  debug=False):
        raise NotImplementedError('CellularAutomata is not implemented yet!')

class DrunkenStumble:
    def create_map(tile_width: int, tile_height: int, sprite_groups: Iterable[Group],  debug=False):
        raise NotImplementedError('CellularAutomata is not implemented yet!')

class ProceduralGenerationType(Enum):
    '''
    BSP -> Binary Space Partition \n
    CA -> Cellular Automata \n
    DS -> Drunken Stumble \n
    '''
    BSP = BinarySpacePartition
    CA = CellularAutomata
    DS = DrunkenStumble

if __name__ == '__main__':
    map, rooms = ProceduralGenerationType.BSP.value.create_map(64, 48, [Group()])
    print('map:')
    for row in map:
        print([int(i) for i in row])

    

