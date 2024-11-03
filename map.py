from enum import IntEnum
from itertools import tee
import random
import sys
from typing import Iterable
from pygame import Rect, sprite
from settings import HEIGHT, WIDTH
from sprites import Wall

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

class Map:
    def __init__(self, sprite_groups: tuple, map_size: tuple[int, int]):
        self.tile_width, self.tile_height = map_size
        self.sprite_groups = sprite_groups
        self.rooms = []
        self.generate_map()

    def pairwise(self, iterable: Iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)
    
    def encase_map(self):
        for x in range(self.tile_width):
            for y in range(self.tile_height):
                if x in (0, self.tile_width-2) or y in (0, self.tile_height-2):
                    Wall(self.sprite_groups, x, y)

    def generate_map(self):
        # self.random(300)
        self.binary_space_partition()
        
    def _get_random_floor(self) -> tuple[int, int]:
            room = random.choice(self.rooms)
            return random.randint(room.x, room.x+room.width), random.randint(room.y, room.y+room.height)

    def get_initial_player_pos(self) -> tuple[int, int]:
        return self._get_random_floor()
    
    def get_mob_positions(self, num_of_positions) -> list[tuple[int, int]]:
        return [self._get_random_floor() for _ in range(num_of_positions)]
    
    def random(self, num_of_walls: int):
        for x in range(self.tile_width):
            for y in range(self.tile_height):
                if x in (0, self.tile_width-2) or y in (0, self.tile_height-2):
                    Wall(self.sprite_groups, x, y)

        for _ in range(num_of_walls):
            x = random.randint(1, self.tile_width)
            y = random.randint(1, self.tile_height)
            Wall(self.sprite_groups, x, y)

    def binary_space_partition(self, debug=False):
        '''
        orderly rooms, dijkstra map to find 
        'essential rooms' and force exploration
        for the sake of progression
        '''
        def make_room(min_splits: int, max_splits: int) -> Room:
            #-1 so they dont spawn in outside walls
            room = Room(1, 1, self.tile_width-1, self.tile_height-1)
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

        def add_room_to_map(room: Room):
            for row in range(room.y, room.y+room.height):
                for col in range(room.x, room.x+room.width):
                    map[row][col] = TileType.Floor

        def create_walls():
            for y, row in enumerate(map):
                for x, tile in enumerate(row):
                    if tile == TileType.Wall:
                        Wall(self.sprite_groups, x, y)

        def encase_map():
            for row in range(self.tile_height):
                for col in range(self.tile_width):
                    if col in (0, self.tile_width-1) or row in (0, self.tile_height-1):
                        map[row][col] = TileType.Wall

        def make_corridor(start: tuple[int, int], finish: tuple[int, int], is_vertical: bool):
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
        
        def add_corridors_to_map():
            for room, room2 in self.pairwise(self.rooms):
                start, finish = room.get_random_tile(), room2.get_random_tile()
                make_corridor(start, finish, is_vertical=bool(random.getrandbits(1)))     
        
        map = [[TileType.Wall for _ in range(self.tile_width)] for _ in range(self.tile_height)]
        NUM_OF_ROOMS = 10
        for i in range(NUM_OF_ROOMS):
            min_splits, max_splits = (3, 5) if i<2 else (5, 6) if i<7 else (4, 8)
            room = make_room(min_splits, max_splits)
            add_room_to_map(room)
            self.rooms.append(room)

            if debug: print('made room of coords:', room)
        
        encase_map()
        add_corridors_to_map()
        if debug:
            print('map:')
            for row in map:
                print([int(i) for i in row])
        create_walls()

    def cellular_automata(self):
        # messy cavern
        # might need to cull unreachable areas
        pass
    
    def drunken_stumble(self):
        # carved out
        pass


class Viewport:
    def __init__(self, tile_width: int, tile_height: int):
        self.viewport = Rect(0, 0, tile_width, tile_height)
        self.tile_width = tile_width
        self.tile_height = tile_height
    
    def apply_offset(self, entity_rect: Rect) -> Rect:
        # watch ep 4 for limiting camera
        # didnt implement it as we dont want 
        # player to know where the map ends anyways
        return entity_rect.move(self.viewport.topleft)
    
    def update(self, target: sprite.Sprite):
        new_x = -target.rect.x + WIDTH//2
        new_y = -target.rect.y + HEIGHT//2
        self.viewport.update(new_x, new_y, self.tile_width, self.tile_height)