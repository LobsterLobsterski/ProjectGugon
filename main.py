import pygame as pg

from GameState import GameState
from gameStates import CombatState, WorldMapState
from settings import HEIGHT, TITLE, WIDTH
from sprites import CombatPlayer, Creature, MobType


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.map_state = WorldMapState(self, self.clock, self.screen)
        self.player = self.map_state.player

        self.current_state = self.map_state

    def run(self):
        self.current_state.run()

    def initiate_combat(self, mob: Creature, player_first: bool):
        self.current_state = CombatState(self, self.clock, self.screen, mob, player_first)
        self.run()

    def enter_world_map(self):
        self.current_state = self.map_state
        self.tun()

if __name__ == '__main__':
    g = Game()
    g.run()
