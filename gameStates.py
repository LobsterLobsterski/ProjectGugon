from enum import Enum
import random
import sys
import pygame as pg

from map import Map, Viewport
from proceduralGeneration import ProceduralGenerationType
from settings import BGCOLOR, BLACK, FPS, GRAY, HEIGHT, LIGHTGREY, TILESIZE, WHITE, WIDTH, YELLOW
from sprites import CombatSkeleton, MobType, Player, Skeleton

class State:
    def __init__(self, game, clock, screen):
        self.game = game
        self.clock = clock
        self.screen = screen
    
    def quit(self):
        pg.quit()
        sys.exit()
     

class WorldMapState(State):
    def __init__(self, game, clock, screen):
        super().__init__(game, clock, screen)

        self.map = []
        self.player_turn = True
        self.mobs = []
        self.new()

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.background_layer = pg.sprite.Group()
        self.interactable_layer = pg.sprite.Group()
        self.player_layer = pg.sprite.Group()
        self.mob_layer = pg.sprite.Group()

        self.map = Map((self.all_sprites, self.background_layer), 
                       (64, 48), map_generator_type=ProceduralGenerationType.BSP)
        
        player_pos_x, player_pos_y = self.map.get_initial_player_pos()
        self.player = Player((self.all_sprites, self.player_layer), 
                             (self.background_layer, self.mob_layer), 
                             player_pos_x, player_pos_y)
        
        mob_positions = self.map.get_mob_positions(1)
        self.mobs = [Skeleton(self, (self.all_sprites, self.mob_layer), x, y, 30, 1, 10) for x, y in mob_positions]

        self.viewport = Viewport(self.map.tile_width, self.map.tile_height)
  
    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        # put this in mob.update() ?
        if not self.player_turn:
            for mob in self.mob_layer:
                mob.act()
            self.player_turn = True
        self.viewport.update(self.player)            
    
    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        self.draw_grid()

        self.draw_mob_paths()

        self.draw_background_sprites()
        self.draw_interactable_sprites()
        self.draw_action_sprites()
        self.draw_turn_depictor()
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

    def draw_turn_depictor(self):
        rect = pg.Rect(0, 0, 50, 50)
        pg.draw.rect(self.screen, BLACK, rect, 2)
        text = pg.font.Font(None, 36).render("1" if self.player_turn else "0", True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
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
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

                if event.key == pg.K_SPACE:
                    self.player_turn = False

                if event.key == pg.K_c:
                    print('pressed c')
                    self.game.change_state(GameState.Combat, MobType.Skeleton)
                    self.game.run()
                
                #when player does an action, switch the turn
                if event.key in [pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN] and self.player_turn and self.player.alive:
                    self.player_turn = False
                    self.player.move(event.key)

       
class CombatState(State):
    def __init__(self, game, clock, screen, monster_type: MobType):
        super().__init__(game, clock, screen)
        self.font = pg.font.Font(None, 36)
        self.player_turn = True
        self.new()

        self.player = self.game.player.get_combat_sprite((self.all_sprites))

        self.generate_encounter(monster_type)

        self.selected_action = None
        self.actions = [
            {"name": "Attack", "rect": pg.Rect(50, HEIGHT-250, 150, 40), "hovered": False},
            {"name": "Defend", "rect": pg.Rect(50, HEIGHT-200, 150, 40), "hovered": False},
            {"name": "Skill", "rect": pg.Rect(50, HEIGHT-150, 150, 40), "hovered": False},
            {"name": "Escape", "rect": pg.Rect(50, HEIGHT-100, 150, 40), "hovered": False}
        ]
        self.target_selection_box = pg.Rect(250, HEIGHT-260, WIDTH-250-50, 200)

    def generate_mob(self, mob_type: MobType, mob_centre: tuple[int, int]):
        if mob_type == MobType.Skeleton:
            CombatSkeleton((self.all_sprites, self.mobs_group), self.player, mob_centre)
        else:
            raise NotImplementedError(f'generation of {mob_type} not implemented yet!')
    
    def generate_encounter(self, mob_type: MobType):
        num_of_enemies = random.randint(1, 4)
        screen_width_per_enemy = WIDTH//num_of_enemies
        enemy_width = 150
        for idx in range(num_of_enemies):
            enemy_midpoint = (2*screen_width_per_enemy*idx + screen_width_per_enemy)//2
            enemy_leftmost_pos = enemy_midpoint-enemy_width//2
            mob_pos = pg.Rect(enemy_leftmost_pos, 100, enemy_width, 50)

            self.generate_mob(mob_type, mob_pos.center)
        
    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.mobs_group = pg.sprite.Group()

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
        if self.selected_action == 'Attack':
            self.update_target_hover(mouse_pos)
            
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

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

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

                if event.key == pg.K_c:
                    self.game.change_state(GameState.Map)
                    self.game.run()
                               
    def update_action_hover(self, mouse_pos):
        for action in self.actions:
            action["hovered"] = action["rect"].collidepoint(mouse_pos)
    
    def update_target_hover(self, mouse_pos):
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
    
    def execute_attack(self, mouse_pos):
        for idx, enemy in enumerate(self.mobs_group):
            target_name_rect = pg.Rect(
                self.target_selection_box.x + 10,
                self.target_selection_box.y + 10 + idx * 40,
                self.target_selection_box.width - 20,
                30
            )
            if enemy.rect.collidepoint(mouse_pos) or target_name_rect.collidepoint(mouse_pos):
                self.player.attack_action(enemy)
                self.player_turn=False
       
    def execute_defend(self):
        self.player.defend_action()
        self.player_turn=False

    def execute_skill(self, mouse_pos):
        self.player.skill_action(mouse_pos)
        self.player_turn=False
    
    def execute_escape(self):
        print('Escapeing')
        self.player_turn=False
        
    ### drawing
    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BLACK)

        self.draw_enemies()
        self.draw_player()
        self.draw_actions()
        self.draw_taget_box()
        self.draw_targets()
        self.draw_turn_depictor()

        pg.display.flip()

    def draw_turn_depictor(self):
        rect = pg.Rect(0, 0, 50, 50)
        pg.draw.rect(self.screen, BLACK, rect, 2)
        text = pg.font.Font(None, 36).render("1" if self.player_turn else "0", True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

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
            if self.selected_action == "Attack":
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
                
    ###
    def update(self):
        if not self.player_turn:
            for enemy in self.mobs_group:
                enemy.fight()

            self.player_turn = True

class MenuState:
    pass
class HubState:
    pass

class GameState(Enum):
    Menu = MenuState
    Hub = HubState
    Map = WorldMapState
    Combat = CombatState