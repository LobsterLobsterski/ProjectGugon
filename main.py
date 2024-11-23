import pygame as pg

from gameStates import GameState
from settings import HEIGHT, TITLE, WIDTH
from sprites import CombatPlayer, MobType


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.map_state = GameState.Map.value(self, self.clock, self.screen)
        self.player = self.map_state.player

        self.current_state = self.map_state

    def run(self):
        self.current_state.run()

    def change_state(self, new_state: GameState, mob_type: MobType):
        if new_state == GameState.Map:
            self.current_state = self.map_state
        
        elif new_state == GameState.Combat:
            self.current_state = new_state.value(self, self.clock, self.screen, mob_type)


if __name__ == '__main__':
    g = Game()
    g.run()
