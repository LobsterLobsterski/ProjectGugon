from math import ceil
import random
import sys
import pygame as pg

from CombatLog import CombatLog
from Dice import Die
from LevelUp import Paladin
from map import Map, Viewport
from proceduralGeneration import ProceduralGenerationType, TileType
from settings import BGCOLOR, BLACK, DARK_GRAY, FPS, GRAY, GREEN, HEIGHT, LIGHTGREY, RED, TILESIZE, WHITE, WIDTH, YELLOW

from sprites import CombatSkeleton, MapExit, MobType, Player, Skeleton, Creature, Wall

class State:
    def __init__(self, game, clock, screen):
        self.game = game
        self.clock = clock
        self.screen = screen
    
    def quit(self):
        pg.quit()
        sys.exit()
     

class LevelUpState(State):
    def __init__(self, game, clock, screen, choices):
        super().__init__(game, clock, screen)
        self.choices = choices
        self.selected_idx = None

        self.card_width, self.card_height = 200, 300
        self.gap = 30
        self.x_start = (WIDTH - ((self.card_width + self.gap) * len(self.choices) - self.gap)) // 2
        self.y_start = 150

    def run(self):
        while True:
            choice = self.events()
            if choice:
                return choice
            
            self.draw()
            # self.clock.tick(FPS)

    def draw(self):
        self.screen.fill(GRAY)

        for idx, choice in enumerate(self.choices):
            x = self.x_start + idx * (self.card_width + self.gap)
            y = self.y_start

            color = (255, 223, 186) if idx == self.selected_idx else (200, 200, 200)
            pg.draw.rect(self.screen, color, (x, y, self.card_width, self.card_height))
            pg.draw.rect(self.screen, BLACK, (x, y, self.card_width, self.card_height), 2)

            # Render text
            font = pg.font.Font(None, 24)
            text_surface = font.render(choice.name, True, BLACK)
            text_rect = text_surface.get_rect(center=(x + self.card_width // 2, y + self.card_height // 2))
            self.screen.blit(text_surface, text_rect)

        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                self.selected_idx = None
                card_width, card_height = 200, 300
                gap = 30
                x_start = (WIDTH - ((card_width + gap) * len(self.choices) - gap)) // 2
                y_start = 150

                for idx in range(len(self.choices)):
                    x = x_start + idx * (card_width + gap)
                    y = y_start
                    if x <= mouse_x <= x + card_width and y <= mouse_y <= y + card_height:
                        self.selected_idx = idx

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.selected_idx is not None:
                    return self.choices[self.selected_idx]

class WorldMapState(State):
    def __init__(self, game, clock, screen):
        super().__init__(game, clock, screen)

        self.map = []
        self.player_turn = True
        self.mobs = []  

        self.new(game)

    def new(self, game):
        self.all_sprites = pg.sprite.Group()
        self.background_layer = pg.sprite.Group()
        self.interactable_layer = pg.sprite.Group()
        self.player_layer = pg.sprite.Group()
        self.mob_layer = pg.sprite.Group()
        self.collision_group = pg.sprite.Group()

        map_type = random.choice(list(ProceduralGenerationType))
        self.map = Map(self.collision_group, self.background_layer,
                       (64, 48), map_generator_type=map_type)
        
        player_pos_x, player_pos_y = self.map.get_initial_player_pos()
        self.player = Player(self.game, (self.all_sprites, self.player_layer), 
                             (self.collision_group, self.mob_layer), 
                             player_pos_x, player_pos_y,
                             Paladin())
        self.player.assign_combat_sprite()
        
        self.map.assign_map_exit((player_pos_x, player_pos_y))
        tile_map = pg.image.load("./assets/Ground/Tilemap_Elevation.png").convert_alpha()
        MapExit(game, (self.all_sprites, self.interactable_layer), tile_map, self.map.exit[0], self.map.exit[1])
        
        mob_positions = self.map.get_mob_positions(1)#(3+(self.game.current_floor-1)*3)
        self.mobs = [Skeleton(game, self.map, self.player, self.all_sprites, self.mob_layer, x, y) for x, y in mob_positions]
        
        self.viewport = Viewport(self.map.tile_width, self.map.tile_height)
  
    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    
    def enemies_act(self):
        for mob in self.mob_layer:
            mob.act()
    
    def update(self):
        self.all_sprites.update()
        if not self.player_turn:
            self.player.tickers_update()
            self.enemies_act()
            self.player_turn = True

        self.viewport.update(self.player)            
    
    def draw(self):
        # pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.draw_background_sprites()
        self.draw_interactable_sprites()
        self.draw_action_sprites()
        self.draw_mob_paths()
        pg.display.flip()

    def draw_mob_paths(self):
        for mob in self.mobs:
            for x, y in mob.path:
                rect = pg.Rect(x, y, TILESIZE//4, TILESIZE//4)
                image = pg.Surface((TILESIZE//4, TILESIZE//4))
                image.fill(YELLOW)
                rec = image.get_rect(center=rect.center)
                rec.x = rec.x*TILESIZE + 3*TILESIZE//8
                rec.y = rec.y*TILESIZE + 3*TILESIZE//8
                self.screen.blit(image, self.viewport.apply_offset(rec))

    def draw_background_sprites(self):
        for sprite in self.background_layer:
            self.screen.blit(sprite.image, self.viewport.apply_offset(sprite.rect))
    
    def draw_interactable_sprites(self):
        for sprite in self.interactable_layer:
            self.screen.blit(sprite.image, self.viewport.apply_offset(sprite.rect))
    
    def draw_action_sprites(self):
        for sprite in self.player_layer:
            self.screen.blit(sprite.image, self.viewport.apply_offset(sprite.rect))
        
        for sprite in self.mob_layer:
            self.screen.blit(sprite.image, self.viewport.apply_offset(sprite.rect))

    def draw_grid(self):
        for vertical_line_pos in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (vertical_line_pos, 0), (vertical_line_pos, HEIGHT))
        for horizontal_line_pos in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, horizontal_line_pos), (WIDTH, horizontal_line_pos))
     
    def events(self):
        e = pg.event.get()
        for event in e:
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

                if event.key == pg.K_SPACE:
                    self.player_turn = False

                if event.key == pg.K_l:
                    self.player.add_experience(600)
                
                #when player does an action, switch the turn
                if self.player_turn and self.player.is_alive:
                    if event.key in [pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN]:
                        self.player_turn = False
                        self.player.move(event.key)

                    elif event.key == pg.K_e:
                        self.player.interact(self.interactable_layer)

       
class CombatState(State):
    def __init__(self, game, clock, screen, map_mob: Creature, player_first: bool):
        super().__init__(game, clock, screen)
        self.font = pg.font.Font(None, 36)

        self.combat_log = CombatLog(
            screen=self.screen,
            rect=pg.Rect(WIDTH-350, HEIGHT-530, 300, 220),
            max_messages=11
        )

        self.player_turn = player_first
        self.map_mob = map_mob
        self.end_screen_timer = None
        self.encounter_experience = 0

        self.mobs_group = pg.sprite.Group()
        self.player = self.game.player.combat_player

        self.generate_encounter(map_mob.mob_type)
        self.get_encounter_experience()

        self.selected_skill = None
        self.selected_action = None
        self.actions = [
            {"name": "Attack", "rect": pg.Rect(50, HEIGHT-250, 150, 40), "hovered": False},
            {"name": "Defend", "rect": pg.Rect(50, HEIGHT-200, 150, 40), "hovered": False},
            {"name": "Skill", "rect": pg.Rect(50, HEIGHT-150, 150, 40), "hovered": False},
            {"name": "Escape", "rect": pg.Rect(50, HEIGHT-100, 150, 40), "hovered": False}
        ]

        self.target_selection_box = pg.Rect(250, HEIGHT-260, WIDTH-250-50, 200)

        self.enemy_turn_queue = []
        self.current_enemy_turn = None
        self.enemy_turn_queue_was_initialised = False


    def get_encounter_experience(self):
        difficult_mod = 1.5+.5*ceil(len(self.mobs_group)/3)
        sum_enemy_exp = sum([mob.get_level()*50 for mob in self.mobs_group])
        self.encounter_experience = sum_enemy_exp*difficult_mod

    def generate_mob(self, mob_type: MobType, mob_centre: tuple[int, int]):
        if mob_type == MobType.Skeleton:
            mob_level = self.game.current_floor
            return CombatSkeleton(self.game, self.mobs_group, self.player, mob_centre, mob_level)
        else:
            raise NotImplementedError(f'[generate_mob] generation of {mob_type} not implemented yet!')
    
    def generate_encounter(self, mob_type: MobType):
        num_of_enemies = 1#random.randint(1, 4)
        screen_width_per_enemy = WIDTH//num_of_enemies
        enemy_width = 150
        
        for idx in range(num_of_enemies):
            enemy_midpoint = (2*screen_width_per_enemy*idx + screen_width_per_enemy)//2
            enemy_leftmost_pos = enemy_midpoint-enemy_width//2
            mob_pos = pg.Rect(enemy_leftmost_pos, 100, enemy_width, 50)

            self.generate_mob(mob_type, mob_pos.center)    

    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    
    ### events
    def events(self):
        mouse_pos = pg.mouse.get_pos()

        self.update_action_hover(mouse_pos)
        self.update_target_hover(mouse_pos)
            
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_k:
                    print('!self kill!')
                    self.player.is_alive = False

            if event.type == pg.MOUSEBUTTONDOWN:
                self.update_selected_action(event.pos)
                
                if self.selected_action == "Attack":
                    self.execute_attack(mouse_pos)

                elif self.selected_action == "Defend":
                    self.execute_defend()

                elif self.selected_action == "Skill":
                    self.execute_skill(mouse_pos)

                elif self.selected_action == "Escape":
                    self.execute_escape()
                               
    def update_action_hover(self, mouse_pos):
        for action in self.actions:
            action["hovered"] = action["rect"].collidepoint(mouse_pos)
    
    def update_target_hover(self, mouse_pos):
        if self.selected_action == "Attack":
            for idx, enemy in enumerate(self.mobs_group):
                target_name_rect = pg.Rect(
                    self.target_selection_box.x + 10,
                    self.target_selection_box.y + 10 + idx * 40,
                    self.target_selection_box.width - 20,
                    30
                )
                enemy.hovered = enemy.rect.collidepoint(mouse_pos) or target_name_rect.collidepoint(mouse_pos)
        
        elif self.selected_action == "Skill":
            if self.selected_skill is None:  # hovering over skills
                for idx, skill in enumerate(self.player.skills):
                    skill_rect = pg.Rect(
                        self.target_selection_box.x + 10,
                        self.target_selection_box.y + 10 + idx * 40,
                        self.target_selection_box.width - 20,
                        30
                    )
                    skill.hovered = skill_rect.collidepoint(mouse_pos)

            else:  # hovering over targets after a skill is selected
                for idx, enemy in enumerate(self.mobs_group):
                    target_name_rect = pg.Rect(
                        self.target_selection_box.x + 10,
                        self.target_selection_box.y + 10 + idx * 40,
                        self.target_selection_box.width - 20,
                        30
                    )
                    enemy.hovered = enemy.rect.collidepoint(mouse_pos) or target_name_rect.collidepoint(mouse_pos)

    def update_selected_action(self, mouse_pos):
        for action in self.actions:
            if action["rect"].collidepoint(mouse_pos):
                self.selected_action = action["name"]
                self.selected_skill = None
    
    def execute_attack(self, mouse_pos):
        for idx, enemy in enumerate(self.mobs_group):
            target_name_rect = pg.Rect(
                self.target_selection_box.x + 10,
                self.target_selection_box.y + 10 + idx * 40,
                self.target_selection_box.width - 20,
                30
            )
            if enemy.rect.collidepoint(mouse_pos) or target_name_rect.collidepoint(mouse_pos):
                attack_data = self.player.attack_action(enemy)
                self.combat_log.add_attack_message(attack_data, 'Player', enemy.name)
                print()

                self.player_turn=False
       
    def execute_defend(self):
        self.player.defend_action()
        self.combat_log.add_defend_message('Player')

        self.player_turn=False

    def execute_skill(self, mouse_pos):
        if self.selected_skill is None:
            for idx, skill in enumerate(self.player.skills):
                skill_name_rect = pg.Rect(
                    self.target_selection_box.x + 10,
                    self.target_selection_box.y + 10 + idx * 40,
                    self.target_selection_box.width - 20,
                    30
                )
                if skill_name_rect.collidepoint(mouse_pos) and not skill.is_ticking():
                    self.selected_skill = skill
                    if skill.target_is_self: 
                        skill_report = self.player.skill_action(skill, self.player)

                        self.combat_log.add_status_effect_message(skill_report, 'Player', 'Player')

                        self.selected_skill = None
                        self.player_turn = False

        else:  # select a target for the skill
            for idx, enemy in enumerate(self.mobs_group):
                target_name_rect = pg.Rect(
                    self.target_selection_box.x + 10,
                    self.target_selection_box.y + 10 + idx * 40,
                    self.target_selection_box.width - 20,
                    30
                )
                if enemy.rect.collidepoint(mouse_pos) or target_name_rect.collidepoint(mouse_pos):
                    report_list = self.player.skill_action(self.selected_skill, enemy)

                    self.combat_log.add_attack_skill_message(report_list, 'Player', enemy.name)

                    self.selected_skill = None
                    self.player_turn = False
    
    def execute_escape(self):
        print('Escapeing...')
        self.combat_log.add_escape_message('Player')
        # temp: add escape on screen and random chance to succeed
        self.exit_combat(False)
        self.player_turn=False

    ### drawing
    def draw(self):
        self.screen.fill(BLACK)

        self.draw_enemies()
        self.draw_player()

        self.draw_ui()

        if self.end_screen_timer is not None:
            if self.player.is_alive:
                self.draw_victory_message()
            else:
                self.draw_defeat_message()

        pg.display.flip()

    def draw_ui(self):
        self.draw_actions()
        self.draw_taget_box()
        self.draw_targets()
        self.draw_status_effect_boxes()
        self.combat_log.draw()

    def draw_enemies(self):
        ### drawing enemies
        for enemy in self.mobs_group:
            if enemy.hovered:
                tinted = enemy.image.copy()
                red_tint = pg.Surface(enemy.image.get_size(), flags=pg.SRCALPHA)
                red_tint.fill((155, 100, 100, 100))
                tinted.blit(red_tint, (0, 0))
                self.screen.blit(tinted, enemy.rect)
            else:
                self.screen.blit(enemy.image, enemy.rect)
     
    def draw_player(self):
        ### drawing player
        self.screen.blit(self.player.image, self.player.rect)

    def draw_actions(self):
        ### drawing actions
        for action in self.actions:
            color = (180, 180, 250) if action["hovered"] or action["name"] == self.selected_action else GRAY
            pg.draw.rect(self.screen, color, action["rect"])
            text = self.font.render(action["name"], True, BLACK)
            self.screen.blit(text, (action["rect"].x + 10, action["rect"].y + 5))
    
    def draw_taget_box(self):
        ### drawing target box
        pg.draw.rect(self.screen, GRAY, self.target_selection_box, 2)
        target_text = self.font.render("Targets", True, WHITE)
        self.screen.blit(target_text, (self.target_selection_box.x + 10, self.target_selection_box.y - 30))

    def draw_targets(self):
        ### drawing targets in taget box
        if self.selected_action == "Attack" or (self.selected_skill and not self.selected_skill.target_is_self):
            for idx, enemy in enumerate(self.mobs_group):
                if enemy.hovered:
                    text_color = (255, 0, 0)
                    background_color = (255, 220, 220)
                    background_rect = pg.Rect(
                        self.target_selection_box.x + 5,
                        self.target_selection_box.y + 5 + idx * 40,
                        self.target_selection_box.width - 10,
                        40
                    )
                    pg.draw.rect(self.screen, background_color, background_rect)
                else:
                    text_color = WHITE

                text = self.font.render(enemy.name, True, text_color)
                self.screen.blit(text, (self.target_selection_box.x + 10, self.target_selection_box.y + 10 + idx * 40))

        elif self.selected_action in [None, "Defence"]:
            # Draw player info in the target box
            player_box = pg.Rect(
                self.target_selection_box.x + 10,
                self.target_selection_box.y + 10,
                self.target_selection_box.width - 20,
                50
            )
            pg.draw.rect(self.screen, (100, 100, 150), player_box)  # Blue-gray color for player box

            # Draw player's health inside the box
            health_text = self.font.render(f"Player Health: {self.player.attributes['health']}/{self.player.attributes['max_health']}", True, WHITE)
            health_text_rect = health_text.get_rect(center=player_box.center)
            self.screen.blit(health_text, health_text_rect)

        elif self.selected_action == "Skill" and not self.selected_skill:
            for idx, skill in enumerate(self.player.skills):
                if skill.is_ticking():  # Grayed-out if skill is on cooldown
                    text_color = DARK_GRAY

                elif skill.hovered:
                    text_color = (255, 0, 0)
                    background_color = (255, 220, 220)
                    background_rect = pg.Rect(
                        self.target_selection_box.x + 5,
                        self.target_selection_box.y + 5 + idx * 40,
                        self.target_selection_box.width - 10,
                        40
                    )
                    pg.draw.rect(self.screen, background_color, background_rect)
                
                else:
                    text_color = WHITE
                    
                skill_text = self.font.render(f'{skill.name} {f"({skill.timer})" if skill.is_ticking() else ""}', True, text_color)
                self.screen.blit(skill_text, (self.target_selection_box.x + 10, self.target_selection_box.y + 10 + idx * 40))

    def draw_status_effect_boxes(self):
        # Helper method to draw status effects for a creature
        def draw_effects(creature):
            if not creature.status_effects:
                return
            
            max_effects = 5  # Limit the number of displayed effects if necessary
            line_height = 20  # Height for each line of text

            for idx, status in enumerate(creature.status_effects[:max_effects]):
                # Position each effect line above the sprite, one above the other
                effect_top = creature.rect.top - 20 - (idx * line_height)
                effect_left = creature.rect.centerx - 50  # Adjust as necessary for width
                effect_width = 100
                effect_height = line_height

                # Draw background for the individual effect
                pg.draw.rect(self.screen, (50, 50, 50), (effect_left, effect_top, effect_width, effect_height))

                # Render the text for the status effect
                effect_text = f"{status.name} ({status.timer})"
                text_surface = pg.font.Font(None, 18).render(effect_text, True, (255, 255, 255))

                # Draw the text centered in the box
                text_rect = text_surface.get_rect(center=(effect_left + effect_width // 2, effect_top + effect_height // 2))
                self.screen.blit(text_surface, text_rect)

        # Draw status effects for the player
        draw_effects(self.player)


        # Draw status effects for each enemy
        for mob in self.mobs_group:
            draw_effects(mob)

    def draw_defeat_message(self):
        text = pg.font.Font(None, 70).render('Defeat...', True, (255, 87, 51))
        self.screen.blit(text, (WIDTH//2, HEIGHT//2))
        
    def draw_victory_message(self):
        text = pg.font.Font(None, 70).render('Victory!', True, (255, 223, 0))
        self.screen.blit(text, (WIDTH//3+text.get_rect().width//2, HEIGHT//4))
    
    ###
    def exit_combat(self, died: bool):
        if died:
            self.game.enter_hub()
        else:
            self.game.enter_world_map()
    
    def init_enemy_queue(self):
        if not self.enemy_turn_queue_was_initialised:
            self.enemy_turn_queue_was_initialised = True
            for enemy in self.mobs_group:
                self.enemy_turn_queue.append(enemy)
    
    def update_bobbing(self):
        ''' 
        update bob animation of current enemy
        and based on that end his turn when
        applicable
        '''
        if self.current_enemy_turn:
            is_bobbing = self.current_enemy_turn.update_bobbing()
            if not is_bobbing:
                self.current_enemy_turn = None

    def check_if_combat_ended(self):
        if len(self.mobs_group) == 0:
            self.map_mob.kill()

            if self.end_screen_timer is None:
                self.end_screen_timer = pg.time.get_ticks()

            elif pg.time.get_ticks() - self.end_screen_timer > 2000:
                self.player.add_experience(self.encounter_experience)
                self.game.player.add_meta_currency(Die(10).roll())
                self.exit_combat(False)
            return True

        elif not self.player.is_alive:
            if self.end_screen_timer is None:
                self.end_screen_timer = pg.time.get_ticks()

            elif pg.time.get_ticks() - self.end_screen_timer > 2000:
                self.player.die()
                self.game.player.die()
                self.exit_combat(True)
            return True

        return False
    
    def execute_current_enemy_turn(self):
        if self.current_enemy_turn is None:
            self.current_enemy_turn = self.enemy_turn_queue.pop(0)
            self.current_enemy_turn.start_bobbing()

            self.current_enemy_turn.receive_damage(self.player.attributes['passive_damage'])
            self.player.receive_damage(self.current_enemy_turn.attributes['passive_damage'])
            enemy_report = self.current_enemy_turn.fight()
            self.combat_log.add_enemy_message(enemy_report, self.current_enemy_turn.name, self.current_enemy_turn.target.name)

            self.current_enemy_turn.update()
            self.current_enemy_turn.tickers_update()
    
    def end_combat_turn(self):
        if not self.enemy_turn_queue and self.enemy_turn_queue_was_initialised:
            self.player.update()
            self.player.tickers_update()
            self.player_turn = True
            self.selected_action = None
            self.enemy_turn_queue_was_initialised = False

    def update(self):
        self.update_bobbing()
        has_combat_ended = self.check_if_combat_ended()
        
        if not self.player_turn and not has_combat_ended:
            self.init_enemy_queue()
            self.execute_current_enemy_turn()
            self.end_combat_turn()


class MenuState:
    pass


class HubState(State):
    def __init__(self, game, clock, screen):
        super().__init__(game, clock, screen)
        self.base_level = 1
        self.player_upgrade_cost = 10
        self.currency = 0

        self.font = pg.font.Font(None, 36)
        self.hub_areas = {
            "Base Upgrades":        {"rect": pg.Rect(100, 100, 200, 50), "hovered": False},
            "Blacksmith":           {"rect": pg.Rect(100, 150, 200, 50), "hovered": False},
            "Trainer":              {"rect": pg.Rect(400, 150, 200, 50), "hovered": False},
            "Temple":               {"rect": pg.Rect(700, 150, 200, 50), "hovered": False},
            "Return to Dungeon":    {"rect": pg.Rect(300, 400, 300, 50), "hovered": False},
        }

        self.base_upgrades = {
            'Blacksmith':   {'rect': pg.Rect(100, 200, 200, 100), 'level': 1, 'hovered': False},
            'Trainer':      {'rect': pg.Rect(350, 200, 200, 100), 'level': 1, 'hovered': False},
            'Temple':       {'rect': pg.Rect(600, 200, 200, 100), 'level': 1, 'hovered': False},
        }

        self.blacksmith_upgrades = {
            'Damage':   {'rect': pg.Rect(100, 200, 200, 100), 'level': 0, 'hovered': False},
            'Defence':  {'rect': pg.Rect(350, 200, 200, 100), 'level': 0, 'hovered': False},
            'Armour':    {'rect': pg.Rect(600, 200, 200, 100), 'level': 0, 'hovered': False},
            'Biteback': {'rect': pg.Rect(850, 200, 200, 100), 'level': 0, 'hovered': False},
        }

        self.trainer_upgrades = {
            'Attack': {'rect': pg.Rect(100, 200, 200, 100), 'level': 0, 'hovered': False},
            'Defence': {'rect': pg.Rect(350, 200, 200, 100), 'level': 0, 'hovered': False},
            'Crit Range': {'rect': pg.Rect(600, 200, 200, 100), 'level': 0, 'hovered': False},
        }

        self.temple_upgrades = {
            'Max Health': {'rect': pg.Rect(100, 200, 200, 100), 'level': 0, 'hovered': False},
            'Regeneration': {'rect': pg.Rect(350, 200, 200, 100), 'level': 0, 'hovered': False},
            'Passive Damage': {'rect': pg.Rect(600, 200, 200, 100), 'level': 0, 'hovered': False},
        }

        self.current_area_name = None
        self.current_area = None
        self.return_button = pg.Rect(300, 500, 200, 50)
        self.return_button_hovered = False

        # For insufficient funds message
        self.insufficient_funds_message = ""
        self.insufficient_funds_alpha = 0

    def get_character_upgrades(self) -> list[tuple[str, int]]:
        upgrades = []
        for upgrade_list in [self.blacksmith_upgrades, self.trainer_upgrades, self.temple_upgrades]:
            upgrades.extend([(upgrade_name.lower().replace(' ', '_'), upgrade['level']) for upgrade_name, upgrade in upgrade_list.items() if upgrade['level']])
        return upgrades
    
    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        mouse_pos = pg.mouse.get_pos()

        # hover effects
        if self.current_area is None:
            for area_name, area in self.hub_areas.items():
                area["hovered"] = area["rect"].collidepoint(mouse_pos)
        else:
            for upgrade_name, upgrade in self.current_area.items():
                upgrade["hovered"] = upgrade['rect'].collidepoint(mouse_pos)

        self.return_button_hovered = self.return_button.collidepoint(mouse_pos)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if self.current_area is None:
                    for area_name, area in self.hub_areas.items():
                        if area["rect"].collidepoint(event.pos):
                            self.handle_selection(area_name)
                else:
                    if self.return_button.collidepoint(event.pos):
                        self.current_area = None
                    else:
                        for upgrade_name, upgrade in self.current_area.items():
                            if upgrade['rect'].collidepoint(event.pos):
                                self.purchase_upgrade(upgrade_name)

    def handle_selection(self, name):
        if name == "Base Upgrades":
            self.current_area_name = 'Base Upgrades'
            self.current_area = self.base_upgrades

        elif name == "Blacksmith":
            self.current_area_name = 'Blacksmith'
            self.current_area = self.blacksmith_upgrades

        elif name == "Trainer":
            self.current_area_name = 'Trainer'
            self.current_area = self.trainer_upgrades

        elif name == "Temple":
            self.current_area_name = 'Temple'
            self.current_area = self.temple_upgrades

        elif name == "Return to Dungeon":
            self.game.return_to_dungeon()

    def purchase_upgrade(self, upgrade_name: str):
        upgrade = self.current_area[upgrade_name]
        cost = self.player_upgrade_cost

        if self.current_area_name != 'Base Upgrades' and upgrade['level'] >= self.base_upgrades[self.current_area_name]['level']:
            self.display_insufficient_funds("Base level too low.")
            return

        if self.currency >= cost:
            self.currency -= cost
            upgrade['level'] += 1
            if self.current_area_name != 'Base Upgrades':
                self.player_upgrade_cost = int(cost * 1.5)
        else:
            self.display_insufficient_funds("Not enough meta-currency!")

    def display_insufficient_funds(self, message):
        self.insufficient_funds_message = message
        self.insufficient_funds_alpha = 255  # Fully visible initially

    def update(self):
        # Gradually fade out the insufficient funds message
        if self.insufficient_funds_alpha > 0:
            self.insufficient_funds_alpha -= 255 * self.dt  # Fades out over 1 second
            if self.insufficient_funds_alpha < 0:
                self.insufficient_funds_alpha = 0

    def draw(self):
        self.screen.fill(DARK_GRAY)

        self.draw_currency_display()

        if self.current_area is None:
            for area_name, area in self.hub_areas.items():
                color = GREEN if area["hovered"] else GRAY
                pg.draw.rect(self.screen, color, area["rect"])
                text = self.font.render(area_name, True, BLACK)
                self.screen.blit(text, (area["rect"].x + 10, area["rect"].y + 10))
        else:
            self.draw_upgrade_menu()

        self.draw_insufficient_funds_message()
        pg.display.flip()

    def draw_currency_display(self):
        currency_text = self.font.render(f"Meta Currency: {self.currency}", True, WHITE)
        self.screen.blit(currency_text, (20, 20))

    def draw_upgrade_menu(self):
        for upgrade_name, upgrade in self.current_area.items():
            upgrade_rect = upgrade['rect']

            if self.current_area_name != 'Base Upgrades' and upgrade['level'] >= self.base_upgrades[self.current_area_name]['level']:
                color = DARK_GRAY  # Locked state
                locked_text = self.font.render("Base level too low", True, RED)
                self.screen.blit(locked_text, (upgrade_rect.x, upgrade_rect.y - 20))
            else:
                color = (180, 180, 250) if upgrade["hovered"] else GRAY

            pg.draw.rect(self.screen, color, upgrade_rect)
            pg.draw.rect(self.screen, BLACK, upgrade_rect, 2)

            # Render upgrade text
            name_text = self.font.render(upgrade_name, True, BLACK)
            level_text = self.font.render(f"Level: {upgrade['level']}", True, BLACK)
            cost = upgrade['level'] * 20 if self.current_area == self.base_upgrades else self.player_upgrade_cost
            cost_text = self.font.render(f"Cost: {cost}", True, BLACK)

            self.screen.blit(name_text, (upgrade_rect.x + 10, upgrade_rect.y + 10))
            self.screen.blit(level_text, (upgrade_rect.x + 10, upgrade_rect.y + 40))
            self.screen.blit(cost_text, (upgrade_rect.x + 10, upgrade_rect.y + 70))

        # Draw Return button
        color = (180, 180, 250) if self.return_button_hovered else GRAY
        pg.draw.rect(self.screen, color, self.return_button)
        return_text = self.font.render("Return", True, BLACK)
        self.screen.blit(return_text, (self.return_button.x + 50, self.return_button.y + 10))

    def draw_insufficient_funds_message(self):
        if self.insufficient_funds_alpha > 0:
            message_surface = self.font.render(self.insufficient_funds_message, True, (255, 0, 0))
            message_surface.set_alpha(int(self.insufficient_funds_alpha))
            self.screen.blit(message_surface, (self.screen.get_width() // 2 - message_surface.get_width() // 2, 50))

    def store_meta_currency(self, number: int):
        self.currency += number

