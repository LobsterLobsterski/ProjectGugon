import pygame as pg
from settings import GREEN, TILESIZE


class Spritesheet:
    def __init__(self, filename, pixel_size):
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
            self.pixel_size = pixel_size
        except pg.error as e:
            raise FileNotFoundError(e)
        
    def image_at(self, sprite_coordinate: tuple) -> pg.Surface:
        x, y = sprite_coordinate
        upscale = 30
        rect = pg.Rect(x*self.pixel_size+upscale+10, y*self.pixel_size+upscale, self.pixel_size-upscale-10, self.pixel_size-upscale)
        try:
            image = self.sheet.subsurface(rect)
        except ValueError as e:
            raise ValueError('Exceeded spritesheet dimensions!', e)
        
        image = pg.transform.scale(image, (TILESIZE*((TILESIZE+upscale)/TILESIZE), TILESIZE*((TILESIZE+upscale)/TILESIZE)))

        return image
    

    # def images_at(self, rects):
    #     "Loads multiple images, supply a list of coordinates" 
    #     return [self.image_at(rect) for rect in rects]
    
class gameObject(pg.sprite.Sprite):
    def __init__(self, groups, image, x, y):
        pg.sprite.Sprite.__init__(self, groups)
        self.image = image
        self.x_pos = x
        self.y_pos = y


class Player(gameObject):
    def __init__(self, game: any, init_x_pos: int, init_y_pos: int):
        self.spritesheet = Spritesheet('assets/Player/Warrior_Red.png', 192)

        gameObject.__init__(self, game.all_sprites, 
                            self.spritesheet.image_at((0, 0)),
                            init_x_pos, init_y_pos
                            )

        self.game = game
        self.rect = self.image.get_rect()

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

class Wall(gameObject):
    def __init__(self, sprite_groups: tuple, x_pos: int, y_pos: int):
        gameObject.__init__(self, sprite_groups, 
                            pg.Surface((TILESIZE, TILESIZE)),
                            x_pos,
                            y_pos
                            )

        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE