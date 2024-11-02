from typing import Any, Iterable
import pygame as pg
from enum import Enum

from settings import GREEN, MOB_SPRITE_SHEET, MOB_SPRITE_SHEET_SPRITE_SIZE, PLAYER_SPRITE_SHEET, PLAYER_SPRITE_SHEET_SPRITE_SIZE, TILESIZE

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Spritesheet:
    def __init__(self, filename, pixel_size):
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
            self.pixel_size = pixel_size
        except pg.error as e:
            raise FileNotFoundError(e)
        
    def image_at(self, sprite_coordinate: tuple, x_offset=10) -> pg.Surface:
        x, y = sprite_coordinate
        crop=30
        rect = pg.Rect(x*self.pixel_size+crop+x_offset, y*self.pixel_size+crop, self.pixel_size-crop-x_offset, self.pixel_size-crop)
        try:
            image = self.sheet.subsurface(rect)
        except ValueError as e:
            raise ValueError('Exceeded spritesheet dimensions!', e)
        
        image = pg.transform.scale(image, (TILESIZE*((TILESIZE+crop)/TILESIZE), TILESIZE*((TILESIZE+crop)/TILESIZE)))

        return image
    

    # def images_at(self, rects):
    #     "Loads multiple images, supply a list of coordinates" 
    #     return [self.image_at(rect) for rect in rects]


class gameObject(pg.sprite.Sprite):
    def __init__(self, groups: Iterable, image: pg.Surface, x: int, y: int):
        pg.sprite.Sprite.__init__(self, groups)
        self.image = image
        self.x_pos = x
        self.y_pos = y
        self.rect = self.image.get_rect()
    
    def place(self, new_x, new_y):
        self.x_pos = new_x
        self.y_pos = new_y


class Player(gameObject):
    def __init__(self, groups: Iterable, collision_layers: tuple, init_x_pos: int, init_y_pos: int):
        self.spritesheet = Spritesheet(PLAYER_SPRITE_SHEET, PLAYER_SPRITE_SHEET_SPRITE_SIZE)

        super().__init__(groups, 
                            self.spritesheet.image_at((0, 0)),
                            init_x_pos, init_y_pos
                            )

        self.collision_layers = collision_layers
        self.direction = Direction.RIGHT

    def move(self, dx=0, dy=0):
        self.change_direction(dx, dy)
        if not self.collision(dx, dy):
            self.x_pos += dx
            self.y_pos += dy
    
    def change_direction(self, dx, dy):
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP
        
    def collision(self, dx=0, dy=0):
        for layer in self.collision_layers:
            for object in layer:
                if object.x_pos == self.x_pos+dx and object.y_pos == self.y_pos+dy:
                    return True

        return False

    def update(self):
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE
        if self.direction == Direction.RIGHT:
            self.image = self.spritesheet.image_at((0, 0))
        elif self.direction == Direction.LEFT:
            self.image = pg.transform.flip(self.spritesheet.image_at((0, 0), x_offset=-30), flip_x=True, flip_y=False)
        if self.direction == Direction.UP:
            self.image = self.spritesheet.image_at((5, 7))
        elif self.direction == Direction.DOWN:
            self.image = self.spritesheet.image_at((5, 5))
        

class Mob(gameObject):
    def __init__(self, groups: Iterable, init_x_pos: int, init_y_pos: int):
        self.spritesheet = Spritesheet(MOB_SPRITE_SHEET, MOB_SPRITE_SHEET_SPRITE_SIZE)
        super().__init__(groups, self.spritesheet.image_at((0, 0)), init_x_pos, init_y_pos)
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE

    def move(self):
        # path find towards player
        pass

    def update(self):
        pass


class Wall(gameObject):
    def __init__(self, sprite_groups: Iterable, x_pos: int, y_pos: int):
        super().__init__(sprite_groups, 
                            pg.Surface((TILESIZE, TILESIZE)),
                            x_pos,
                            y_pos
                            )

        self.image.fill(GREEN)
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE