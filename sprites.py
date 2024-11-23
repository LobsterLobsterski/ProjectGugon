import random
import sys
from typing import Any, Callable, Dict, Iterable
import pygame as pg
from enum import Enum

from AI.BehaviourTree import BehaviourTree
from Pathfinding import Pathfinder
from settings import GREEN, GRIDHEIGHT, GRIDWIDTH, TILESIZE
from utils import get_squared_distance


class MobType(Enum):
    '''
    Player\n
    Goblin\n
    Skeleton\n
    '''
    Player = 0
    Goblin = 1
    Skeleton = 2

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Spritesheet:
    def __init__(self, mob_type: MobType):
        filename, pixel_size = self.get_spritesheet_data(mob_type)
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
            self.pixel_size = pixel_size
        except pg.error as e:
            raise FileNotFoundError(e)
        
    def get_spritesheet_data(self, mob_type: MobType) -> tuple[str, int]:
        if mob_type == MobType.Player:
            return 'assets/Player/Warrior_Red.png', 192
        elif mob_type == MobType.Goblin:
            return 'assets/Mob/Torch_Yellow.png', 192
        elif mob_type == MobType.Skeleton:
            return 'assets/Mob/Skeleton.png', 16
        else:
            raise ValueError(f'Mob {mob_type} has no spritesheet defined!')
        
    def image_at(self, sprite_coordinate: tuple, x_offset=10) -> pg.Surface:
        x, y = sprite_coordinate
        crop=30
        if self.pixel_size == 192:
            rect = pg.Rect(x*self.pixel_size+crop+x_offset, y*self.pixel_size+crop, self.pixel_size-crop-x_offset, self.pixel_size-crop)
        else:
            rect = pg.Rect(x*self.pixel_size, y*self.pixel_size, self.pixel_size, self.pixel_size)
        try:
            image = self.sheet.subsurface(rect)
        except ValueError as e:
            raise ValueError(f'Exceeded spritesheet dimensions!: {e}')
        
        if self.pixel_size == 192:
            image = pg.transform.scale(image, (TILESIZE*((TILESIZE+crop)/TILESIZE), TILESIZE*((TILESIZE+crop)/TILESIZE)))
        else:
            image = pg.transform.scale(image, (TILESIZE, TILESIZE) )

        return image
    
    def get_sprite(self, row: int, col: int) -> pg.Surface:
        rect = pg.Rect(self.pixel_size*row,
                       self.pixel_size*col,
                       self.pixel_size,
                       self.pixel_size
        )
        return self.sheet.subsurface(rect)


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
        print(self.id, 'received', damage, 'damage!')
        self.health -= damage
        if self.health <= 0:
            print(self.id, 'died!')
            self.die()
    
    def die(self):
        self.alive = False
        # this removes the sprite from sprite
        # groups and thus stops it from being
        # drawn
        self.kill()
        # self.spawn_corpse()

      
class CombatMob:
    def __init__(self):
        pass


class Player(Creature):
    def __init__(self, groups: Iterable, collision_layers: tuple, init_x_pos: int, init_y_pos: int):
        self.spritesheet = Spritesheet(MobType.Player)

        super().__init__(groups, 
                            self.spritesheet.image_at((0, 0)),
                            init_x_pos, init_y_pos,
                            100, 1, 10
                            )

        self.collision_layers = collision_layers
        self.direction = Direction.RIGHT

    def get_combat_sprite(self):
        self.skills = ['skill1', 'skill2']
        return CombatPlayer(self.health, self.damage, self.skills)
    
    def simple_attack(self, target: Creature):
        if isinstance(target, Creature):
            print(f'Player attacked {target}')
            target.receive_damage(self.damage)
    
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
        collision_object = self.collision(dx, dy)

        if collision_object is None:
            self.x_pos += dx
            self.y_pos += dy
        else:
            self.simple_attack(collision_object)
    
    def change_direction(self, dx, dy):
        if dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP
        
    def collision(self, dx=0, dy=0) -> GameObject:
        for layer in self.collision_layers:
            for object in layer:
                if object.x_pos == self.x_pos+dx and object.y_pos == self.y_pos+dy:
                    return object

        return None

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
        

class CombatPlayer:
    def __init__(self, health: int, damage: int, skills: list):
        self.spritesheet = Spritesheet(MobType.Player)
        self.image = self.spritesheet.get_sprite(5, 7)
        self.rect = pg.Rect(50, 400, 100, 50)
        self.health = health
        self.damage = damage
        self.skills = skills
        
    def attack(self, target: CombatMob):
        print('player attacked', target.name)

    def defend(self):
        print('player defended')

    def skill(self, selected):
        print('player skilled!', selected)


class MapMob(Creature):
    def __init__(self, game, groups: Iterable, init_x_pos: int, init_y_pos: int, health:int, attack_range:int, damage:int, mob_type: MobType):
        self.spritesheet = Spritesheet(mob_type)
        
        super().__init__(groups, self.spritesheet.image_at((0, 0)), 
                         init_x_pos, init_y_pos,
                         health, attack_range, damage)
        
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE
        self.game = game
        self.pathfinder = Pathfinder(game.map)
        ### separate class?
        self.path = []
        self.path_iterator = iter(self.path)
        ###
        self.last_known_player_pos = self.game.player.get_position()
    
    def fight(self):
        raise NotImplementedError('Enemy cannot fight yet!')
    
    def act(self):
        if self.alive:
            print(f'\n{type(self).__name__} {self.id} acts:')

            action = self.bahaviour_tree.find_action()
            action()
        
    ###basic behaviour actions
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

    ###basic behaviour conditions
    def detect_player(self) -> bool:
        #temp, for now mobs have global awareness
        #of player as long as they're alive
        return self.game.player.alive
    
    def in_attack_range(self) -> bool:
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
    
    def init_behaviour(self, behaviour_tree: Dict[Callable, Callable]) -> BehaviourTree:
        return BehaviourTree(self, behaviour_tree)
    
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


class Goblin(MapMob):
    def __init__(self, game, groups: Iterable, init_x_pos: int, init_y_pos: int, health:int, attack_range:int, damage:int):
        super().__init__(game, groups, init_x_pos, init_y_pos, health, attack_range, damage, MobType.Goblin)

        behaviour_tree = {
            self.detect_player: [self.roam, self.in_attack_range], 
            self.in_attack_range: [self.follow_path, self.attack]
        }
        self.bahaviour_tree = super().init_behaviour(behaviour_tree)
    
    ### complex/specific  behaviour actions
    ###
    ### complex/specific conditions
    ###


class Skeleton(MapMob):
    def __init__(self, game, groups: Iterable, init_x_pos: int, init_y_pos: int, health:int, attack_range:int, damage:int):
        super().__init__(game, groups, init_x_pos, init_y_pos, health, attack_range, damage, MobType.Skeleton)

        behaviour_tree = {
            self.detect_player: [self.roam, self.in_attack_range], 
            self.in_attack_range: [self.follow_path, self.attack]
        }
        self.bahaviour_tree = self.init_behaviour(behaviour_tree)

        def get_combat_skeleton(self):
            return CombatSkeleton(self.health, self.damage)


class CombatSkeleton(CombatMob):
    skeleton_counter=0
    def __init__(self, health: int, damage: int):
        super().__init__()
        self.spritesheet = Spritesheet(MobType.Skeleton)
        
        self.image = self.spritesheet.get_sprite(random.randint(0, 2), 0)
        self.image = pg.transform.scale(self.image, (128, 128))

        self.rect = self.image.get_rect()
        self.health = health
        self.damage = damage

        CombatSkeleton.skeleton_counter+=1
        self.name = f"Skeleton {self.skeleton_counter}"
        self.hovered = False

    def fight(self):
        print(self.name, 'is fighting!!!')
        
        
    def attack(self, target):
        print('skeleton attacked', target)
    def defend(self):
        print('skeleton defended')
    def skill(self):
        print('skeleton skilled!')


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
