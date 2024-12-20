import pygame as pg

from Dice import Die
from gameStates import CombatState, HubState, LevelUpState, WorldMapState
from settings import HEIGHT, TITLE, WIDTH
from sprites import Creature


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.map_state = WorldMapState(self, self.clock, self.screen)
        self.current_floor = 1
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
        self.current_floor += 1
        self.map_state = WorldMapState(self, self.clock, self.screen)
        # temp: arbitrary number
        self.player.add_experience(600)
        self.player.add_meta_currency(Die(20).roll())
        self.enter_world_map()

    def return_to_dungeon(self):
        self.current_floor = 1
        upgrades = self.hub_state.get_character_upgrades()
        self.map_state = WorldMapState(self, self.clock, self.screen)
        self.player = self.map_state.player
        self.player.apply_upgrades(upgrades)
        self.enter_world_map()
    
    def enter_level_up_selection(self, choices):
        state = LevelUpState(self, self.clock, self.screen, choices)
        selected_choice = state.run()
        return selected_choice

    def enter_hub(self):
        print('player has procured:', self.player.meta_currency, 'meta currency during this run!')
        self.hub_state.store_meta_currency(self.player.meta_currency)
        self.current_state = self.hub_state
        self.run()

if __name__ == '__main__':
    g = Game()
    g.run()
