import pygame as pg
from settings import *

class Player(pg.sprite.Sprite):
    def __init__(self, game: any, init_x_pos: int, init_y_pos: int):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.x_pos = init_x_pos
        self.y_pos = init_y_pos

    def move(self, dx=0, dy=0):
        if not self.wall_collision(dx, dy):
            self.x_pos += dx
            self.y_pos += dy

    def wall_collision(self, dx=0, dy=0):
        for wall in self.game.walls:
            if wall.x_pos == self.x_pos+dx and wall.y_pos == self.y_pos+dy:
                return True
        
        return False

    def update(self):
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE

class Wall(pg.sprite.Sprite):
    def __init__(self, sprite_groups: tuple, x_pos: int, y_pos: int):
        self.groups = sprite_groups

        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE