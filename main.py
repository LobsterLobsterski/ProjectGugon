import pygame as pg

from gameStates import GameState
from settings import HEIGHT, TITLE, WIDTH


class Game:                   
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.map_state = GameState.Map.value(self, self.clock, self.screen)
        self.current_state = self.map_state

    def run(self):
        self.current_state.run()

    def change_state(self, new_state: GameState):
        if new_state == GameState.Map:
            self.current_state = self.map_state
            return
        
        self.current_state = new_state.value(self, self.clock, self.screen)


if __name__ == '__main__':
    g = Game()
    g.run()
