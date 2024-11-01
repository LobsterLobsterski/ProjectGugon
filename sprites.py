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
        self.x_pos += dx
        self.y_pos += dy

    def update(self):
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE

class Wall(pg.sprite.Sprite):
    def __init__(self, game: any, x_pos: int, y_pos: int):
        self.groups = game.all_sprites, game.walls

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE