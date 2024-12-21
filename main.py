import pygame as pg
import random
from Dice import Die
from gameStates import CombatState, HubState, LevelUpState, WorldMapState
from settings import HEIGHT, TITLE, WIDTH
from sprites import Creature


class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()  # Initialize the mixer
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(100, 100)
        self.current_floor = 1

        self.init_music()

        self.map_state = WorldMapState(self, self.clock, self.screen)
        self.hub_state = HubState(self, self.clock, self.screen)

        self.player = self.map_state.player
        self.current_state = self.map_state

        # Start with WorldMap music
        self.play_music("world_map")

    def init_music(self):
        relative_path = './assets/Music/'
        self.music_tracks = {
            "world_map": relative_path+"world_map_music.mp3",
            "combat": relative_path+"combat_music.mp3",
            "hub": relative_path+"hub_music.mp3",
        }

        self.current_track = None  # Currently loaded track
    
    def play_music(self, track_name):
        pg.mixer.music.stop()

        track_path = self.music_tracks[track_name]
        if self.current_track != track_path:
            pg.mixer.music.load(track_path)
            self.current_track = track_path

        random_start = random.uniform(0, 3600)
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.1)
        pg.mixer.music.set_pos(random_start)

    def run(self):
        self.current_state.run()

    def initiate_combat(self, mob: Creature, player_first: bool):
        self.play_music("combat")  # Switch to combat music
        self.current_state = CombatState(self, self.clock, self.screen, mob, player_first)
        self.run()

    def enter_world_map(self):
        self.play_music("world_map")  # Switch to WorldMap music
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
        self.play_music("hub")  # Switch to Hub music
        print('player has procured:', self.player.meta_currency, 'meta currency during this run!')
        self.hub_state.store_meta_currency(self.player.meta_currency)
        self.current_state = self.hub_state
        self.run()


if __name__ == '__main__':
    g = Game()
    g.run()