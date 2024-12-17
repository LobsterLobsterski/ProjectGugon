import random


class Die:
    def __init__(self, size: int):
        self.size = size
    
    def roll(self) -> int:
        return random.randint(1, self.size)
    
class DiceGroup:
    def __init__(self, dice: list[Die]):
        self.dice = dice

    def roll(self):
        return sum([die.roll() for die in self.dice])
    
    def add_die(self, die: Die):
        self.dice.append(die)
    
    def add_dice(self, dice: list[Die]):
        self.dice += dice