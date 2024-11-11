import random
import sys
from typing import Any, Iterable
import pygame as pg
from enum import Enum

from AI.BehaviourTree import BehaviourTree
from Pathfinding import Pathfinder
from settings import GREEN, GRIDHEIGHT, GRIDWIDTH, MOB_SPRITE_SHEET, MOB_SPRITE_SHEET_SPRITE_SIZE, PLAYER_SPRITE_SHEET, PLAYER_SPRITE_SHEET_SPRITE_SIZE, TILESIZE
from utils import get_squared_distance

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

class GameObject(pg.sprite.Sprite):
    number_of_obejects=0
    def __init__(self, groups: Iterable, image: pg.Surface, x: int, y: int):
        pg.sprite.Sprite.__init__(self, groups)
        self.image = image
        self.x_pos = x
        self.y_pos = y
        self.rect = self.image.get_rect()
        self.id = GameObject.number_of_obejects
        GameObject.number_of_obejects+=1

    def place(self, new_x: int, new_y: int):
        self.x_pos = new_x
        self.y_pos = new_y

    def place(self, new_pos: tuple[int, int]):
        self.x_pos = new_pos[0]
        self.y_pos = new_pos[1]

    def get_position(self)->tuple[int, int]:
        return self.x_pos, self.y_pos

class Creature(GameObject):
    def __init__(self, groups: Iterable, image: pg.Surface, x: int, y: int, health: int, range: int, damage: int):
        super().__init__(groups, image, x, y)
        self.health = health
        self.attack_range = range
        self.damage = damage
        self.alive = True

    def receive_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            print(self.id, 'died!')
            self.alive = False
        

class Player(Creature):
    def __init__(self, groups: Iterable, collision_layers: tuple, init_x_pos: int, init_y_pos: int):
        self.spritesheet = Spritesheet(PLAYER_SPRITE_SHEET, PLAYER_SPRITE_SHEET_SPRITE_SIZE)

        super().__init__(groups, 
                            self.spritesheet.image_at((0, 0)),
                            init_x_pos, init_y_pos,
                            100, 1, 10
                            )

        self.collision_layers = collision_layers
        self.direction = Direction.RIGHT

    def move(self, key: pg.event):
        dx, dy = 0, 0
        if key == pg.K_LEFT:
           dx=-1
        if key == pg.K_RIGHT:
            dx=1
        if key == pg.K_UP:
            dy=-1
        if key == pg.K_DOWN:
            dy=1

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
        

class Mob(Creature):
    def __init__(self, game, groups: Iterable, init_x_pos: int, init_y_pos: int):
        self.spritesheet = Spritesheet(MOB_SPRITE_SHEET, MOB_SPRITE_SHEET_SPRITE_SIZE)
        super().__init__(groups, self.spritesheet.image_at((0, 0)), 
                         init_x_pos, init_y_pos,
                         15, 1, 100)
        
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE
        self.game = game
        self.pathfinder = Pathfinder(game.map)
        ### separate class?
        self.path = []
        self.path_iterator = iter(self.path)
        ###
        self.last_known_player_pos = self.game.player.get_position()

        self.bahaviour_tree = self.init_behaviour()
    

    def act(self):
        if self.alive:
            print(f'\nMob {self.id} acts:')

            action = self.bahaviour_tree.find_action()
            print('action found:', action)
            action()
            # sys.exit()
            # self.follow_path()
        
    ###actions
    def follow_path(self):
        print('\tfollows path')
        try:
            new_pos = next(self.path_iterator)
        except StopIteration:
            self.path = []
            return
        
        if self.check_collisions(new_pos):
            return
        
        self.place(new_pos)

    def attack(self):
        print('\tAttacking!')
        self.path = []
        self.game.player.receive_damage(self.damage)
   
    def roam(self):
        print('\tRoaming!')
        if not self.path:
            goal = self.get_random_valid_roam_goal()
            self.update_path(goal)

        self.follow_path()
    ###

    ### conditions
    def detect_player(self) -> bool:
        #temp, for now mobs have global awareness
        #of player as long as they're alive
        return self.game.player.alive
    
    def in_attack_range(self) -> bool:
        print('own pos: ', self.get_position(), 'lkpp:', self.last_known_player_pos)
        ### needs to be here otherwise the mob doesn't refind path after attacking
        self.update_path(self.last_known_player_pos)
        return get_squared_distance(self.get_position(), self.last_known_player_pos) <= self.attack_range
    ###

    def get_random_valid_roam_goal(self, distance=5):
        x = random.randint(self.x_pos-distance, self.x_pos+distance)
        y = random.randint(self.y_pos-distance, self.y_pos+distance)
        print(x, y)
        x = int(min(GRIDHEIGHT, max(0, x)))
        y = int(min(GRIDWIDTH, max(0, y)))
        print('get_random_valid_roam_goal:', x, y)
        print('w, h:', GRIDWIDTH, GRIDHEIGHT)
        if self.game.map.check_if_pos_is_floor((x, y)):
            return x, y

        return self.get_random_valid_roam_goal(distance)
    

    def init_behaviour(self) -> BehaviourTree:
        tree = {
            self.detect_player: [self.roam, self.in_attack_range], 
            self.in_attack_range: [self.follow_path, self.attack]
        }
        return BehaviourTree(self, tree)
    

    def update_last_known_player_pos(self):
        self.last_known_player_pos = self.game.player.get_position()

    def update_path(self, goal: tuple[int, int]):
        if ( self.game.player.alive and self.player_has_moved() ) \
                or not self.game.player.alive \
                or not self.path:
            
            self.update_last_known_player_pos()
            self.path = self.pathfinder.find_path(self.get_position(), goal)[1:]
            self.path_iterator = iter(self.path)
    
    def player_has_moved(self):
        return self.last_known_player_pos != self.game.player.get_position()
    
    def move(self, dx=0, dy=0):
        # print('\tMob movement')
        self.x_pos += dx
        self.y_pos += dy

    def check_collisions(self, new_pos: tuple[int, int]):
        #temp
        return False
    
    def update(self):
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE


class Wall(GameObject):
    def __init__(self, sprite_groups: Iterable, x_pos: int, y_pos: int):
        super().__init__(sprite_groups, 
                            pg.Surface((TILESIZE, TILESIZE)),
                            x_pos,
                            y_pos
                            )

        self.image.fill(GREEN)
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE