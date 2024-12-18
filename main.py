import pygame as pg

from GameState import GameState
from gameStates import CombatState, HubState, LevelUpState, WorldMapState
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
        self.hub_state = HubState(self, self.clock, self.screen)

        self.player = self.map_state.player
        

        self.current_state = self.map_state
 
    def run(self):
        self.current_state.run()

    def initiate_combat(self, mob: Creature, player_first: bool): 
        self.current_state = CombatState(self, self.clock, self.screen, mob, player_first)
        self.run()

    def enter_world_map(self):
        self.current_state = self.map_state
        self.run()

    def enter_new_level(self):
        self.map_state = WorldMapState(self, self.clock, self.screen)
        # temp: arbitrary number
        self.player.add_experience(600)
        self.enter_world_map()

    def return_to_dungeon(self):
        self.map_state = WorldMapState(self, self.clock, self.screen)
        self.player = self.map_state.player
        self.enter_world_map()
    
    def enter_level_up_selection(self, choices):
        state = LevelUpState(self, self.clock, self.screen, choices)
        selected_choice = state.run()
        return selected_choice

    def enter_hub(self):
        self.current_state = self.hub_state
        self.run()

if __name__ == '__main__':
    g = Game()
    g.run()
