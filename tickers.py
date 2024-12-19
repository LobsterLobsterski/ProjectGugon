import random
from typing import Callable

from Dice import DiceGroup, Die

class Ticker:
    def __init__(self, round_timer: int):
        self.timer = round_timer
    
    def is_ticking(self):
        return self.timer > 0
    
    def update(self):
        if self.is_ticking():
            self.timer-=1

class Skill(Ticker):
    def __init__(self, name, target_is_self, effect: callable, cooldown):
        super().__init__(0)
        self.name = name
        self.effect = effect
        self.cooldown = cooldown
        self.hovered = False
        self.target_is_self = target_is_self

    def activate(self, target, self_target) -> dict:
        self.timer = self.cooldown
        return self.effect(target, self_target)
        
    
    def __repr__(self):
        return f'Skill({self.name})'

class AttackSkill(Skill):
    def __init__(self, name, target_is_self, effect, cooldown):
        super().__init__(name, target_is_self, effect, cooldown)


class StatusEffect(Ticker):
    def __init__(self, name, effects: list[tuple[str, int]] | Callable, duration):
        super().__init__(duration)
        self.name = name
        self.effects = effects
    
    def apply_effect(self, target) -> list[tuple[str, int]]:
        target.status_effects.append(self)
        # print('[StatusEffect] applying', self.effects, 'to', target)
        for effect in self.effects:
            if isinstance(effect, Callable):
                effect(target.passive_skills)
                continue

            effect_stat, stat_change = effect

            if effect_stat == 'damage_dice': #its a list
                if isinstance(stat_change, Die):
                    target.attributes['damage_dice'].add_die(stat_change)
                elif isinstance(stat_change, DiceGroup):
                    target.attributes['damage_dice'].add_dice(stat_change)
                continue

            target.attributes[effect_stat] += stat_change
        
        return self.effects

    def remove_effect(self, target):
        for effect in self.effects:
            effect_stat, effect_value = effect

            if effect_stat == 'damage_dice':
                target.attributes['damage_dice'].remove(effect_value)
                continue

            if effect_stat == 'temporary_health':
                target.attributes['temporary_health'] = 0

            target.attributes[effect_stat] -= effect_value

    def update(self):
        super().update()

    def  __eq__(self, value: str) -> bool:
        return self.name == value
    
    def __repr__(self) -> str:
        return f'StatusEffect(name={self.name}, turns_left={self.timer})'

class Distract(Skill):
    def __init__(self, cooldown=3):
        super().__init__('Distract', False, Distract.effect, cooldown)

    def effect(target, *args) -> dict:
        effects = StatusEffect('Distracted', [('defence', -10)], 0).apply_effect(target)
        return {'name': 'Distracted',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }

class Rampage(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=5):
        def effect(target, self_target):
            StatusEffect('Out of Position', [('defence', -20)], 3).apply_effect(self_target)
            StatusEffect('Out of Position', [('attack', -15)], 0).apply_effect(self_target)

            for _ in range(3):
                attack_method(target)

        super().__init__('Rampage', False, effect, cooldown)

class Smite(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=4):
        def effect(target, self_target):
            StatusEffect('Smite', [('damage_dice', DiceGroup([Die(8), Die(8)]))], 0).apply_effect(self_target)
            attack_method(target)

        super().__init__('Smite', False, effect, cooldown)

class Bless(Skill):
    def __init__(self, cooldown=5):
        super().__init__('Bless', True, Bless.effect, cooldown)

    def effect(target, *args):
        effects = StatusEffect('Blessed', [('attack', 2), ('damage_dice', Die(4))], 4).apply_effect(target)
        return {'name': 'Blessed',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }

class TripleSlash(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=3):
        def effect(target, *args):
            for _ in range(3):
                attack_method(target)

        super().__init__('Triple Slash', False, effect, cooldown)

class Heal(Skill):
    def __init__(self, cooldown=10):
        super().__init__('Heal', True, Heal.effect, cooldown)

    def effect(target, *args):
        amount = DiceGroup([Die(8), Die(8)]).roll()
        target.heal(amount)
        return {'name': 'Heal',
                'effects': {{'stat': 'health', 'value': amount}}
                }

class Agathys(Skill):
    def __init__(self, cooldown=20):
        super().__init__('Armour of Agathys', True, Agathys.effect, cooldown)

    def effect(target, *args):
        # TEMP: damage needs to be swapped for biteback and health for temporary_health
        effects = StatusEffect('Armour of Agathys', [('temporary_health', 5), ('biteback', 5)], 5).apply_effect(target)
        return {'name': 'Armour of Agathys',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }

class InvincibleConqueror(Skill):
    def __init__(self, cooldown=100):
        super().__init__('Invincible Conqueror', True, InvincibleConqueror.effect, cooldown)

    def effect(target, *args):
        effects = StatusEffect('Invincible Conqueror', [('resistance', 1), ('attack_number', 1), ('crit_range', -1)], 10).apply_effect(target)
        return {'name': 'Invincible Conqueror',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }

class ShieldOfFaith(Skill):
    def __init__(self, cooldown=40):
        super().__init__('Shield of Faith', True, ShieldOfFaith.effect, cooldown)

    def effect(target, *args):
        effects = StatusEffect('Shield of Faith', [('defence', 2)], 10).apply_effect(target)
        return {'name': 'Shield of Faith',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }
        
class SacredWeapon(Skill):
    def __init__(self, cooldown=40):
        super().__init__('Sacred Weapon', True, SacredWeapon.effect, cooldown)

    def effect(target, *args):
        effects = StatusEffect('Sacred Weapon', [('damage_dice', Die(8))], 15).apply_effect(target)
        return {'name': 'Sacred Weapon',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }

class HolyNimbus(Skill):
    def __init__(self, cooldown=100):
        super().__init__('Holy Nimbus', True, HolyNimbus.effect, cooldown)

    def effect(target, *args):
        effects = StatusEffect('Holy Nimbus', [('defence', 2), ('armour', 2), ('passive_damage', 10)], 10).apply_effect(target)
        return {'name': 'Holy Nimbus',
                'effects': [{'stat': stat, 'value': value} for stat, value in effects]
                }

list_of_all_skills = [Distract, 
                      Rampage, 
                      Smite, 
                      Bless, 
                      TripleSlash,
                      Heal,
                      Agathys,
                      ShieldOfFaith
                    ]


def get_epic_boons():
    return [
        StatusEffect('Boon of Fortitude', [('max_health', 40), ('health', 40)], -1),
        StatusEffect('Boon of Recovery', [('health', 40), ('regeneration', 1)], -1),
        StatusEffect('Boon of Combat Prowess', [('attack', 100)], -1),# temp: only for first attack of turn
        StatusEffect('Boon of Spell Recall', [('defence', 1)], -1),# temp: one random skill goes off cooldown at the start of the turn
    ]

def get_random_skills(number):
    return [random.choice(list_of_all_skills) for _ in range(number)]