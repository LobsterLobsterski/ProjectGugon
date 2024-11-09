import pygame as pg
import sys

from Pathfinding import Pathfinder
from map import Map, Viewport
from settings import BGCOLOR, BLACK, FPS, HEIGHT, LIGHTGREY, TILESIZE, TITLE, WHITE, WIDTH, YELLOW
from sprites import Mob, Player

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.player_turn = True

        self.mobs = []

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.background_layer = pg.sprite.Group()
        self.interactable_layer = pg.sprite.Group()
        self.player_layer = pg.sprite.Group()
        self.mob_layer = pg.sprite.Group()

        self.map = Map((self.all_sprites, self.background_layer), 
                       (64, 48))
        
        player_pos_x, player_pos_y = self.map.get_initial_player_pos()
        self.player = Player((self.all_sprites, self.player_layer), 
                             (self.background_layer, self.mob_layer), 
                             player_pos_x, player_pos_y)
        mob_positions = self.map.get_mob_positions(1)
        self.mobs = [Mob(self, (self.all_sprites, self.mob_layer), x, y) for x, y in mob_positions]

        self.viewport = Viewport(self.map.tile_width, self.map.tile_height)
  
    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
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
                
                #when player does an action, switch the turn
                if event.key in [pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN] and self.player_turn:
                    self.player_turn = False
                    self.player.move(event.key)
                
    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


if __name__ == '__main__':
    g = Game()
    g.show_start_screen()
    while True:
        g.new()
        g.run()
        g.show_go_screen()