from __future__ import annotations
import random


class Die:
    def __init__(self, size: int):
        self.size = size
    
    def roll(self, crit_roll=False) -> int:
        number_of_rolls = 2 if crit_roll else 1
        return sum([random.randint(1, self.size) for _ in range(number_of_rolls)])
    
    def __repr__(self):
        return f'1d{self.size}'
    
class DiceGroup:
    def __init__(self, dice: list[Die]):
        self.dice = dice

    def roll(self, crit_roll=False):
        return sum([die.roll(crit_roll) for die in self.dice])
    
    def add_die(self, die: Die):
        self.dice.append(die)
    
    def add_dice(self, dice_group: DiceGroup):
        self.dice += dice_group.dice

    def remove(self, die: Die):
        self.dice.remove(die)

    def __repr__(self):
        buckets = {}
        for die in self.dice:
            if die.size not in buckets:
                buckets[die.size] = 1
            else:
                buckets[die.size] += 1
        
        return ' and '.join([f'{number}d{die_size}' for die_size, number in buckets.items()])
        