import random
from pygame import Rect, sprite
from settings import HEIGHT, WIDTH
from proceduralGeneration import ProceduralGenerationType, TileType, Room
from Pathfinding import Pathfinder


class Map:
    def __init__(self, collision_group: sprite.Group, background_group: sprite.Group, map_size: tuple[int, int], map_generator_type: ProceduralGenerationType):
        self.tile_width, self.tile_height = map_size
        self.collision_group = collision_group
        self.background_group = background_group
        self.rooms = []
        self.map = []
        self.generator = map_generator_type.value
        self.generate_map()
        self.exit = ...

    def generate_map(self):
        self.map, self.rooms = self.generator.create_map(self.tile_width, self.tile_height, self.collision_group, self.background_group)

    def assign_map_exit(self, player_pos: tuple[int, int]):
        potential_exit = self._get_random_floor()
        p = Pathfinder(self)
        while not p.find_path(player_pos, potential_exit):
            potential_exit = self._get_random_floor()

        self.exit = potential_exit

    
    def check_if_pos_is_floor(self, pos: tuple[int, int]) -> bool:
        # print('floor type:', self.map[pos[0]][pos[1]], self.map[pos[0]][pos[1]] == TileType.Floor)
        return self.map[pos[0]][pos[1]] == TileType.Floor
    
    def _get_random_floor(self) -> tuple[int, int]:
            y = random.randint(0, self.tile_height-1)
            row = self.map[y]
            available_tiles = [(x, y) for x, tile in enumerate(row) if tile == TileType.Floor]

            return random.choice(available_tiles) if len(available_tiles)>0 else self._get_random_floor()

    def get_initial_player_pos(self) -> tuple[int, int]:
        return self._get_random_floor()
    
    def get_mob_positions(self, num_of_positions) -> list[tuple[int, int]]:
        return [self._get_random_floor() for _ in range(num_of_positions)]

    def getMapArray(self) -> list[list[TileType]]:
        return self.map

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