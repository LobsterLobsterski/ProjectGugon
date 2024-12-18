import random


class Die:
    def __init__(self, size: int):
        self.size = size
    
    def roll(self, crit_roll=False) -> int:
        number_of_rolls = 2 if crit_roll else 1
        return sum([random.randint(1, self.size) for _ in range(number_of_rolls)])
    
class DiceGroup:
    def __init__(self, dice: list[Die]):
        self.dice = dice

    def roll(self, crit_roll=False):
        return sum([die.roll(crit_roll) for die in self.dice])
    
    def add_die(self, die: Die):
        self.dice.append(die)
    
    def add_dice(self, dice: list[Die]):
        self.dice += dice

    def remove(self, die: Die):
        self.dice.remove(die)