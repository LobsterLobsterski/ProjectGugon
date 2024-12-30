from __future__ import annotations
import random
from typing import Callable, Dict, Iterable
import pygame as pg
from enum import Enum

from AI.BehaviourTree import BehaviourTree
from Dice import DiceGroup, Die
from LevelUp import ClassTable, SkeletonClass
from Pathfinding import Pathfinder
from settings import GREEN, GRIDHEIGHT, GRIDWIDTH, RED, TILESIZE
from tickers import Skill, StatusEffect
from utils import get_squared_distance

def get_tile(tile_map, x, y, tile_size=TILESIZE):
    rect = pg.Rect(x*tile_size, y*tile_size, tile_size, tile_size)
    return tile_map.subsurface(rect)

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

    def place(self, new_pos: tuple[int, int]):
        self.x_pos = new_pos[0]
        self.y_pos = new_pos[1]

    def get_position(self)->tuple[int, int]:
        return self.x_pos, self.y_pos

    def apply_tint(self, color):
        """Apply a tint to the surface (light brown for example)."""
        tint_surface = pg.Surface(self.image.get_size())
        tint_surface.fill(color + (0,))  # Add transparency value (0 = fully opaque)
        
        # Blend the tint with the original image using alpha blending
        self.image.blit(tint_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

    # temp: needs to be here as its the closest ancestor of both combat creature and map mob
    def init_behaviour(self, behaviour_tree: Dict[Callable, Callable]) -> BehaviourTree:
        return BehaviourTree(self, behaviour_tree)
    

class Wall(GameObject):
    def __init__(self, sprite_groups: Iterable, tile_map, x_pos: int, y_pos: int):
        super().__init__(sprite_groups, 
                            get_tile(tile_map, 1, 5),
                            x_pos,
                            y_pos
                            )
        # self.image.fill(GREEN)
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE


class Floor(GameObject):
    def __init__(self, sprite_groups: Iterable, tile_map, x_pos: int, y_pos: int):
        # Get the original floor tile from the tile map
        floor_texture = get_tile(tile_map, 1, 1)

        # Apply a brown tint to the floor texture (adjust the RGBA values as needed)
        self.image = floor_texture.copy()
        # self.apply_tint((132, 123, 109))
        self.apply_tint((120, 105, 90))

        super().__init__(sprite_groups, self.image, x_pos, y_pos)

        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE


class MapExit(GameObject):
    def __init__(self, game, sprite_groups: Iterable, tile_map, x_pos: int, y_pos: int):
        floor_texture = get_tile(tile_map, 1, 7)

        self.image = floor_texture.copy()
        self.apply_tint((255, 150, 150))

        super().__init__(sprite_groups, 
                            self.image,
                            x_pos,
                            y_pos
                            )

        # self.image.fill(RED)
        self.rect.x = x_pos * TILESIZE
        self.rect.y = y_pos * TILESIZE
        self.game = game
    
    def interact(self):
        self.game.enter_new_level()

class Creature(GameObject):
    def __init__(self, game, groups: Iterable, image: pg.Surface, x: int, y: int, health: int, damage: int, attack: int, defence: int, armour: int, damage_dice: DiceGroup, class_table: ClassTable):
        super().__init__(groups, image, x, y)
        self.game = game
        self.attributes = {
            'max_health': health,
            'health': health,
            'temporary_health': 0,
            'hit_die': Die(8), # temp: should depend on class
            'damage': damage,
            'damage_dice': damage_dice, # temp: should depend on class/items
            'attack': attack,
            'crit_range': 20,
            'attack_number': 1, # number of attacks made per attack action
            'defence': defence,
            'armour': armour,
            'passive_damage': 0,
            'biteback': 0,
            'regeneration': 0,
            'resistance': 0

        }
        self.experience = 0
        self.status_effects = []
        self.passive_skills = []
        self.class_table = class_table
        self.subclass = None
        self.skills =  []

        self.is_alive = True

        ### bobing
        self.original_y = ...
        self.bob_timer = None
        self.bob_duration = 300
        self.bob_offset = -10

    def add_experience(self, experience_points: int):
        self.experience += experience_points
        if self.experience >= self.class_table.next_experience_threshold():
            self.level_up()

    def level_up(self) -> type:
        hp_increase = self.attributes['hit_die'].roll()
        self.attributes['max_health'] += hp_increase
        self.attributes['health'] += hp_increase

        gains = self.class_table.level_up()
        for gain in gains:
            if isinstance(gain, list):
                gain = self.game.enter_level_up_selection(gain)

            if issubclass(type(gain), ClassTable):
                self.subclass = gain
                self.class_table.subclass = gain
                gain = self.class_table.subclass_levelup()

            # temp: this shouldn't be a thing
            if isinstance(gain, str) and gain == 'subclass_levelup':
                gain = self.class_table.subclass_levelup()

            elif isinstance(gain, Skill):
                self.skills.append(gain)

            elif isinstance(gain, StatusEffect):
                self.passive_skills.append(gain)
                gain.apply_effect(self)

            elif isinstance(gain, tuple):
                stat, amount = gain
                self.attributes[stat] += amount

        return gains
        
    def get_level(self) -> int:
        return self.class_table.level
    
    def receive_damage(self, damage: int) -> int:
        damage = max(0, damage - self.attributes['armour'])
        if not damage:
            return 0
        
        if self.attributes['resistance']:
            damage //= 2

        self.attributes['temporary_health'] -= damage
        if self.attributes['temporary_health'] >= 0:
            return 0

        damage = self.attributes['temporary_health']*-1
        self.attributes['temporary_health'] = 0
        
        self.attributes['health'] -= damage
        if self.attributes['health'] <= 0:
            print(self.id, 'died!')
            self.die()

        return damage
    
    def deal_damage(self, target: Creature, is_crit: bool) -> dict[str, int]:
        # temp: split into each dice for better reporting
        roll = self.attributes['damage_dice'].roll(is_crit)
        damage =  roll + self.attributes['damage']
        target_recieved_damage = target.receive_damage(damage)
        self_received_damage = self.receive_damage(target.attributes['biteback'])

        return {'dealt': {'damage_roll': roll, 'damage_bonus': self.attributes['damage'], 'total_received': target_recieved_damage}, 'received': self_received_damage}

    def die(self):
        self.is_alive = False
        self.kill()
        # self.spawn_corpse()
            
    def heal(self, amount: int):
        if not amount:
            return
        
        self.attributes['health'] = min(self.attributes['health']+amount, self.attributes['max_health'])
    
    def tickers_update(self):
        for s in self.status_effects:
            s.update()
            if not s.is_ticking():
                self.status_effects.remove(s)
                s.remove_effect(self)

            self.heal(self.attributes['regeneration'])

    def start_bobbing(self):
        '''
        Initiates the bobbing animation
        '''
        self.bob_timer = pg.time.get_ticks()
        self.original_y = self.rect.y

    def update_bobbing(self) -> bool:
        '''
        updates the bob animation and
        returns bool indicating whether or not
        creature is still bobbing
        '''
        if self.bob_timer is None:
            return False

        elapsed = pg.time.get_ticks() - self.bob_timer
        if elapsed < self.bob_duration:
            # Calculate interpolation between original_y and bob_offset
            progress = elapsed / self.bob_duration
            if progress < 0.5:
                self.rect.y = self.original_y + self.bob_offset * progress * 2  # Bob up
            else:
                self.rect.y = self.original_y + self.bob_offset * (2 - progress * 2)  # Bob down
        else:
            # Reset after animation
            self.rect.y = self.original_y
            self.bob_timer = None
        
        return True
    
    def update(self):
        pass


class Player(Creature):
    def __init__(self, game, groups: Iterable, collision_layers: tuple, init_x_pos: int, init_y_pos: int, classTable: ClassTable):
        self.spritesheet = Spritesheet(MobType.Player)

        super().__init__(game, groups, 
                            self.spritesheet.image_at((0, 0)),
                            init_x_pos, init_y_pos,
                            50, 5, 7, 18, 1, DiceGroup([Die(8)]),
                            classTable
                            )

        self.name = 'Player'
        self.collision_layers = collision_layers
        self.direction = Direction.RIGHT
        self.combat_player = None
        self.meta_currency = 100 # meta currency

    def apply_upgrades(self, upgrades: list[tuple[str, int]]):
        for stat, level in upgrades:
            if stat == 'max_health':
                self.attributes['max_health'] += DiceGroup([self.attributes['hit_die'] for _ in range(level)]).roll()
                self.attributes['health'] = self.attributes['max_health']
                continue

            if stat == 'crit_range':
                stat*=1
            
            self.attributes[stat] += level

    def add_meta_currency(self, number: int):
        print(f'gained {number} meta currency!')
        self.meta_currency += number
    
    def assign_combat_sprite(self, groups: tuple[pg.sprite.Group] = ()):
        self.combat_player = CombatPlayer(self.game, groups, self.collision_layers, 0, 0, self.attributes, self.skills, self.class_table)
        self.class_table.init_attack_method(self.combat_player.make_attack)
        self.level_up()
 
    def interact(self, interactable_layer: pg.sprite.Group):
        interactable_pos_x, interactable_pos_y = self.x_pos, self.y_pos
        if self.direction == Direction.LEFT:
            interactable_pos_x-=1
        elif self.direction == Direction.RIGHT:
            interactable_pos_x+=1
        elif self.direction == Direction.UP:
            interactable_pos_y-=1
        else:
            interactable_pos_y+=1
        
        for object in interactable_layer:
            if object.x_pos == interactable_pos_x and object.y_pos == interactable_pos_y or object.x_pos == self.x_pos and object.y_pos == self.y_pos:
                object.interact()
                return
  
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

        elif isinstance(collision_object, MapMob):
            self.engage(collision_object)
    
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

    def engage(self, mob):
        self.game.initiate_combat(mob, True)
        
    def update(self):
        super().update()
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

    def tickers_update(self):
        super().tickers_update()
        for s in self.skills:
            s.update()   


class CombatPlayer(Player):
    def __init__(self, game, groups, collision_layers, init_x_pos, init_y_pos, attributes, skills, classTable):
        super().__init__(game, groups, collision_layers, init_x_pos, init_y_pos, classTable)
        self.rect = pg.Rect(50, 400, 100, 50)
        self.image = self.spritesheet.get_sprite(5, 7)
        self.skills = skills
        self.attributes = attributes
    
    def make_attack(self, target: Creature) -> dict[str, any]:
        roll = Die(20).roll()
        is_crit = roll >= self.attributes['crit_range']
        is_hit = roll+self.attributes['attack'] >= target.attributes['defence']
        damage_roll_info = {'dealt': {'damage_roll': 0, 'damage_bonus': 0, 'total_received': 0}, 'received': 0}
        if is_hit:
            damage_roll_info = self.deal_damage(target, is_crit)

        return {'is_hit': is_hit, 'is_crit': is_crit, 'roll': roll, 'attack_bonus': self.attributes['attack'], 'damage': damage_roll_info}
    
    def attack_action(self, target: Creature) -> list[dict]:
        attack_data = []
        for _ in range(self.attributes['attack_number']):
            results = self.make_attack(target)
            attack_data.append(results)

        return results
    
    def defend_action(self):
        status_effect = StatusEffect("Defence", [('defence', 10)], 1)
        self.status_effects.append(status_effect)
        return status_effect.apply_effect(self)

    def skill_action(self, selected_skill: Skill, target: Creature) -> dict:
        return selected_skill.activate(target, self)

    def tickers_update(self):
        super().tickers_update()
        for s in self.skills:
            s.update()

    def add_meta_currency(self, number):
        return super().add_meta_currency(number)
        
    # same as creature to ignore Player class update loop
    def update(self):
        pass

class MapMob(GameObject):
    def __init__(self, game, map, player, all_sprites_groups: pg.sprite.Group, all_map_mobs_group: pg.sprite.Group, init_x_pos: int, init_y_pos: int, mob_type: MobType):
        self.spritesheet = Spritesheet(mob_type)
        
        super().__init__((all_sprites_groups, all_map_mobs_group), self.spritesheet.image_at((0, 0)), 
                         init_x_pos, init_y_pos,
                         )
        
        self.all_map_mobs = all_map_mobs_group
        self.mob_type = mob_type
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE
        self.game = game
        self.map = map
        self.player = player

        self.pathfinder = Pathfinder(self.map)
        ### separate class?
        self.path = []
        self.path_iterator = iter(self.path)
        ###
        self.last_known_player_pos = self.player.get_position()
      
    def act(self):
        action = self.bahaviour_tree.find_action()
        action()
        
    ###basic behaviour actions
    def follow_path(self):
        try:
            new_pos = next(self.path_iterator)
        except StopIteration:
            self.path = []
            return
        
        if self.check_collisions(new_pos):
            return
        
        self.place(new_pos)

    def engage(self):
        self.path = []
        self.game.initiate_combat(self, False)
   
    def roam(self):
        if not self.path:
            goal = self.get_random_valid_roam_goal()
            self.update_path(goal)

        self.follow_path()
    ###

    ###basic behaviour conditions
    def detect_player(self) -> bool:
        # 8 squares range
        return get_squared_distance(self.player.get_position(), self.get_position()) < 64
        # return self.player.is_alive
    
    def in_engage_range(self) -> bool:
        ### needs to be here otherwise the mob doesn't refind path after attacking
        self.update_path(self.last_known_player_pos)
        return get_squared_distance(self.get_position(), self.last_known_player_pos) <= 1
    ###

    def get_random_valid_roam_goal(self, distance=5):
        x = random.randint(self.x_pos-distance, self.x_pos+distance)
        y = random.randint(self.y_pos-distance, self.y_pos+distance)
        x = int(min(GRIDWIDTH, max(0, x)))
        y = int(min(GRIDHEIGHT, max(0, y)))
        try:
            if self.map.check_if_pos_is_floor((x, y)):
                return x, y
        except:
            print('x, y', x, y)
            exit()

        return self.get_random_valid_roam_goal(distance)
    
    def update_last_known_player_pos(self):
        self.last_known_player_pos = self.player.get_position()

    def update_path(self, goal: tuple[int, int]):
        if self.player.is_alive and self.player_has_moved() \
                or not self.player.is_alive \
                or not self.path:
            
            self.update_last_known_player_pos()
            self.path = self.pathfinder.find_path(self.get_position(), goal)[1:]
            self.path_iterator = iter(self.path)
    
    def player_has_moved(self):
        return self.last_known_player_pos != self.player.get_position()
    
    def move(self, dx=0, dy=0):
        self.x_pos += dx
        self.y_pos += dy

    def check_collisions(self, new_pos: tuple[int, int]):
        for mob in self.all_map_mobs:
            if mob.get_position() == new_pos:
                return True
        return False
    
    def update(self):
        self.rect.x = self.x_pos * TILESIZE
        self.rect.y = self.y_pos * TILESIZE

    def kill(self):
        self.path = []
        super().kill()
    

class Goblin(MapMob):
    def __init__(self, game, groups: Iterable, init_x_pos: int, init_y_pos: int):
        super().__init__(game, groups, init_x_pos, init_y_pos, MobType.Goblin)

        behaviour_tree = {
            self.detect_player: [self.roam, self.in_engage_range], 
            self.in_engage_range: [self.follow_path, self.engage]
        }
        self.bahaviour_tree = self.init_behaviour(behaviour_tree)
    
    ### complex/specific  behaviour actions
    ###
    ### complex/specific conditions
    ###


class Skeleton(MapMob):
    def __init__(self, game, map, player, all_sprites_groups: pg.sprite.Group, all_map_mobs_group: pg.sprite.Group, init_x_pos: int, init_y_pos: int):
        super().__init__(game, map, player, all_sprites_groups, all_map_mobs_group, init_x_pos, init_y_pos, MobType.Skeleton)

        behaviour_tree = {
            self.detect_player: [self.roam, self.in_engage_range], 
            self.in_engage_range: [self.follow_path, self.engage]
        }
        self.bahaviour_tree = self.init_behaviour(behaviour_tree)

class CombatCrature(Creature):
    def __init__(self, game, player: CombatPlayer, mobs_group: pg.sprite.Group, 
                 image: pg.Surface, x: int, y: int, mob_counter: int, 
                 health: int, damage: int, attack: int, defence: int, armour: int, 
                 dice: DiceGroup, class_table: ClassTable):
        super().__init__(game, (mobs_group, ), image, x, y, health, damage, attack, defence, armour, dice, class_table)
        self.all_combat_mobs = mobs_group
        self.name = f"{type(self).__name__.replace('Combat', '')} {mob_counter}"
        self.hovered = False
        self.player = player
        # for now only target is player
        self.target = self.player

        ### related to skills
        # dict of skill-name to skill-name, keys replace values
        self.skill_replace_dict = {}
        '''
        skill name to list of:
            previous_node: callable,
                after what node does this new sub tree go
            connect_to_prev_on_true: bool,
                is this sub-tree connected to the previous node
                on the on-true statement (2nd element of list)?
            next_node: callable,
                what node do we connect to on sub-tree exit
            connect_to_next_on_true: bool
                is this sub-trees exit located on the 
                on-true of the root (2nd element of list)?

        so this means that now, when skeleton gains necrotic strikes
        after is alone evaluates true we'll consider the necrotic strikes
        condition instead of the rampage condition. When evaluated it will be executed
        if it evals to True and exit to is_rampage_off_cooldown on false.
        '''
        self.modify_behaviour_tree_dict = {}

        # temp: because of the btd we need to do first level up before initing btd
        self.level_up()

        # key: [on_false, on_true]
        # has the initial collection of collables needed to construct a behaviour tree
        self.behaviour_tree_dict = {}
        ###

    def make_attack(self, target: Creature) -> dict[str, any]:
        roll = Die(20).roll()
        is_crit = roll >= self.attributes['crit_range']
        is_hit = roll+self.attributes['attack'] >= target.attributes['defence']
        damage_roll_info = {'dealt': {'damage_roll': 0, 'damage_bonus': 0, 'total_received': 0}, 'received': 0}
        if is_hit:
            damage_roll_info = self.deal_damage(target, is_crit)

        return {'is_hit': is_hit, 'is_crit': is_crit, 'roll': roll, 'attack_bonus': self.attributes['attack'], 'damage': damage_roll_info}

    def attack_action(self, target: Creature, *args) -> list[dict]:
        attack_data = []
        for _ in range(self.attributes['attack_number']):
            results = self.make_attack(target)
            attack_data.append(results)

        return results
    
    def defend_action(self, target, *args):###
        status_effect = StatusEffect("Defence", [('defence', 10)], 1)
        self.status_effects.append(status_effect)
        return status_effect.apply_effect(self)
    
    def modify_behaviour_tree(self, gain: Skill):
        previous_node, connect_to_prev_on_true, next_node, connect_to_next_on_true = self.modify_behaviour_tree_dict[gain.name]

        condition_node = lambda *args: not gain.is_ticking()
        execution_node = lambda self_target, target, *args: gain.activate(target, self_target)
        # create subtree
        if connect_to_next_on_true:
            array = [execution_node, next_node]
        else:
            array = [next_node, execution_node]

        sub_tree = {condition_node: array}
        
        # add subtree and connect it
        if previous_node is None:
            sub_tree.update(self.behaviour_tree_dict)
            self.behaviour_tree_dict = sub_tree
        else:
            self.behaviour_tree_dict.update(sub_tree)
            prev_node_connection_idx = int(connect_to_prev_on_true)
            self.behaviour_tree_dict[previous_node][prev_node_connection_idx] = condition_node

    def replace_skill(self, gain):
        if gain.name in self.skill_replace_dict:
            for skill in self.skills:
                if skill.name == self.skill_replace_dict[gain.name]:
                    self.skills.remove(skill)
                    break
    
    def level_up(self):
        gains = super().level_up()
        for gain in gains:
            self.replace_skill(gain)
            if isinstance(gain, Skill):
                if gain.name in self.modify_behaviour_tree_dict:
                    self.modify_behaviour_tree(gain)

        print('CombatSkeleton levelup: skills;', self.skills)

    def tickers_update(self):
        super().tickers_update()
        for s in self.skills:
            s.update()


class CombatSkeleton(CombatCrature):
    skeleton_counter=0
    def __init__(self, game, mobs_group: pg.sprite.Group, player: CombatPlayer, centre: tuple[int, int], level=1):
        self.spritesheet = Spritesheet(MobType.Skeleton)
        CombatSkeleton.skeleton_counter+=1
        super().__init__(game, player, mobs_group, self.spritesheet.get_sprite(random.randint(0, 2), 0), 
                         0, 0, self.skeleton_counter,
                         13, 3, 5, 13, 0, DiceGroup([Die(6)]), 
                         SkeletonClass(self.make_attack))
        
        self.all_combat_mobs = mobs_group
        self.image = pg.transform.scale(self.image, (128, 128))
        self.rect = self.image.get_rect(center=centre)

        # triple slash replaces ramage
        self.skill_replace_dict = {
            'Triple Slash': 'Rampage'
        }
        
        self.modify_behaviour_tree_dict = {
            # 'Rampage': [self.is_alone, True, self.attack_action, False],
            # 'Distract': [self.is_alone, False, self.is_rampage_off_cooldown, False],
            'Necrotic Strikes': [self.is_alone, True, self.is_rampage_off_cooldown, False],
            'Armour of Agathys': [None, None, self.is_alone, False]
        }

        # basic skeleton bt
        self.behaviour_tree_dict = {
            self.is_alone: [self.is_opponent_distracted, self.is_rampage_off_cooldown],
            self.is_opponent_distracted: [self.is_distract_off_cooldown, self.is_rampage_off_cooldown], 
            self.is_distract_off_cooldown: [self.is_rampage_off_cooldown, self.skills[0].activate],
            self.is_rampage_off_cooldown: [self.attack_action, self.skills[1].activate]
        }

        for _ in range(level-1):
            self.level_up()

        self.bahaviour_tree = self.init_behaviour(self.behaviour_tree_dict)


    def fight(self) -> dict:
        self.start_bobbing()
        action = self.bahaviour_tree.find_action()
        return action(self.target, self)

    ### conditions
    def is_alone(self):
        return len(self.all_combat_mobs) == 1
    def is_opponent_distracted(self):
        return 'Distracted' in self.player.status_effects
    def is_distract_off_cooldown(self):
        return not self.skills[0].is_ticking()
    def is_rampage_off_cooldown(self):
        return not self.skills[1].is_ticking()
    ###
