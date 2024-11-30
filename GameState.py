from enum import Enum


class GameState(Enum):
    '''
    Menu\nHub\nMap\nCombat
    '''
    Menu = 1
    Hub = 2
    Map = 3
    Combat = 4