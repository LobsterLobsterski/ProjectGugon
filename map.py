import random
from pygame import Rect, sprite
from settings import HEIGHT, WIDTH
from sprites import Wall


class Map:
    def __init__(self, sprite_groups: tuple, map_size=(32, 24)):
        self.tile_width, self.tile_height = map_size
        self.generate_map(sprite_groups)

    def generate_map(self, sprite_groups: tuple) -> list:
        #TODO: procedural generation
        for x in range(self.tile_width):
            for y in range(self.tile_height):
                if x in (0, self.tile_width-1) or y in (0, self.tile_height-1):
                    Wall(sprite_groups, x, y)
        for _ in range(300):
            x = random.randint(1, self.tile_width)
            y = random.randint(1, self.tile_height)
            Wall(sprite_groups, x, y)


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