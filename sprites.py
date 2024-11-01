import pygame as pg
from settings import *

class Spritesheet:
    def __init__(self, filename):
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
        except pg.error as e:
            raise FileNotFoundError(e)
        
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        # temp for current sprite sheet
        rectangle = list(rectangle)
        rectangle[0]+=40
        rectangle[1]+=30
        rectangle[2]-=40
        rectangle[3]-=40
        #### 

        rect = pg.Rect(rectangle)#.scale_by(1-64/150, 1-64/150)
        image = self.sheet.subsurface(rect)
        # image = pg.Surface(rect.size).convert_alpha()
        image = pg.transform.scale(image, (64, 64))
        # image.blit(self.sheet, (0, 0), rect)

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image
    

    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    

class Player(pg.sprite.Sprite):
    def __init__(self, game: any, init_x_pos: int, init_y_pos: int):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.spritesheet = Spritesheet('assets/Player/Warrior_Red.png')
        
        self.game = game
        self.image = self.spritesheet.image_at((0, 0, 150, 150))#pg.Surface((TILESIZE, TILESIZE))
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