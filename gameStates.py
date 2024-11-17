from enum import Enum
import sys
import pygame as pg

from map import Map, Viewport
from proceduralGeneration import ProceduralGenerationType
from settings import BGCOLOR, BLACK, FPS, GRAY, HEIGHT, LIGHTGREY, TILESIZE, WHITE, WIDTH, YELLOW
from sprites import Player, Skeleton

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
                       (64, 48), map_generator_type=ProceduralGenerationType.CA)
        
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
                    self.game.change_state(GameState.Combat)
                    self.game.run()
                
                #when player does an action, switch the turn
                if event.key in [pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN] and self.player_turn and self.player.alive:
                    self.player_turn = False
                    self.player.move(event.key)

       
class CombatState(State):
    def __init__(self, game, clock, screen):
        super().__init__(game, clock, screen)
        self.font = pg.font.Font(None, 36)
        self.player_turn = True

        self.enemies = [
            pg.Rect(0, 100, 150, 50),
            pg.Rect(0, 100, 150, 50),
            pg.Rect(0, 100, 150, 50)
        ]
        self.centre_enemies()

        self.player = pg.Rect(50, 400, 100, 50)  # Player box
        self.actions = [
            {"name": "Attack", "rect": pg.Rect(50, HEIGHT-250, 150, 40), "hovered": False},
            {"name": "Defend", "rect": pg.Rect(50, HEIGHT-200, 150, 40), "hovered": False},
            {"name": "Skill", "rect": pg.Rect(50, HEIGHT-150, 150, 40), "hovered": False},
            {"name": "Escape", "rect": pg.Rect(50, HEIGHT-100, 150, 40), "hovered": False}
        ]
        self.target_selection_box = pg.Rect(250, HEIGHT-260, WIDTH-250-50, 200)

        self.new()

    def centre_enemies(self):
        screen_width_per_enemy = WIDTH//len(self.enemies)
        start_pos = 0
        for enemy_rect in self.enemies:
            enemy_rect.left = (start_pos+screen_width_per_enemy)//2
            start_pos += screen_width_per_enemy+enemy_rect.width
    
    def new(self):
        pass

    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
    
    def events(self):
        mouse_pos = pg.mouse.get_pos()

        for action in self.actions:
            action["hovered"] = action["rect"].collidepoint(mouse_pos)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.MOUSEBUTTONDOWN:
                for action in self.actions:
                    if action["rect"].collidepoint(event.pos):
                        print(f"{action['name']} clicked!")

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

                if event.key == pg.K_c:
                    self.game.change_state(GameState.Map)
                    self.game.run()

                if event.key == pg.K_SPACE:
                    print('select button')
                    self.player_turn = False
                
                if event.key == pg.K_LEFT:
                    print('left')

                if event.key == pg.K_RIGHT:
                    print('right')

                if event.key == pg.K_UP:
                    print('up')

                if event.key == pg.K_DOWN:
                    print('down')
                             
    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BLACK)

        self.draw_mobs()
        self.draw_ui()

        self.draw_turn_depictor()
        pg.display.flip()

    def draw_turn_depictor(self):
        rect = pg.Rect(0, 0, 50, 50)
        pg.draw.rect(self.screen, BLACK, rect, 2)
        text = pg.font.Font(None, 36).render("1" if self.player_turn else "0", True, WHITE)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_mobs(self):
        pass

    def draw_ui(self):
        for idx, monster in enumerate(self.enemies):
            pg.draw.rect(self.screen, GRAY, monster)
            text = self.font.render(f"Monster {idx + 1}", True, BLACK)
            self.screen.blit(text, (monster.x + 10, monster.y + 10))
        
        pg.draw.rect(self.screen, GRAY, self.player)
        player_text = self.font.render("Player", True, BLACK)
        self.screen.blit(player_text, (self.player.x + 10, self.player.y + 10))

        for action in self.actions:
            color = (180, 180, 250) if action["hovered"] else GRAY
            pg.draw.rect(self.screen, color, action["rect"])
            text = self.font.render(action["name"], True, BLACK)
            self.screen.blit(text, (action["rect"].x + 10, action["rect"].y + 5))
        
        pg.draw.rect(self.screen, GRAY, self.target_selection_box, 2)
        target_text = self.font.render("Targets", True, BLACK)
        self.screen.blit(target_text, (self.target_selection_box.x + 10, self.target_selection_box.y - 30))
        
    def update(self):
        if not self.player_turn:
            for enemy in self.enemies:
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