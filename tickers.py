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
    
    def apply_effect(self, target) -> dict:
        # target.status_effects.append(self)
        # print('[StatusEffect] applying', self.effects, 'to', target)
        for effect in self.effects:
            if isinstance(effect, Callable):
                effect(target.passive_skills)
                continue

            effect_stat, stat_change = effect

            if effect_stat == 'damage_dice': 
                if isinstance(stat_change, Die):
                    target.attributes['damage_dice'].add_die(stat_change)
                elif isinstance(stat_change, DiceGroup):
                    target.attributes['damage_dice'].add_dice(stat_change)
                continue

            target.attributes[effect_stat] += stat_change
        
        return {'name': self.name,
                'effects': [{'stat': stat, 'value': value} for stat, value in self.effects],
                'target': target.name
                }

    def remove_effect(self, target):
        for effect in self.effects:
            effect_stat, effect_value = effect

            if effect_stat == 'damage_dice':
                dice = effect_value.dice if isinstance(effect_value, DiceGroup) else [effect_value]
                for die in dice:
                    target.attributes['damage_dice'].remove(die)
                    
                continue

            if effect_stat == 'temporary_health':
                target.attributes['temporary_health'] = 0
                continue

            target.attributes[effect_stat] -= effect_value

    def update(self):
        super().update()

    def  __eq__(self, value: str) -> bool:
        return self.name == value
    
    def __repr__(self) -> str:
        return f'StatusEffect(name={self.name}, turns_left={self.timer})'

class Rampage(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=5):
        def effect(target, self_target) -> list[dict]:
            print('rampage used: target, self_target', target, self_target)
            report = {'name': 'Rampage', 'Status Effects': [], 'Attacks': []}

            status_effect_1 = StatusEffect('Out of Position: Defence', [('defence', -5)], 3)
            status_effect_2 = StatusEffect('Out of Position: Attack', [('attack', -5)], 0)

            raport1 = status_effect_1.apply_effect(self_target)
            raport2 = status_effect_2.apply_effect(self_target)

            self_target.status_effects.append(status_effect_1)
            self_target.status_effects.append(status_effect_2)

            report['Status Effects'] = [raport1, raport2]
            for _ in range(3):
                report['Attacks'].append(attack_method(target))
            
            return report
            

        super().__init__('Rampage', False, effect, cooldown)

class Smite(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=4):
        def effect(target, self_target):
            report = {'name': 'Smite', 'Status Effects': [], 'Attacks': []}
            status_effect = StatusEffect('Smite', [('damage_dice', DiceGroup([Die(8), Die(8)]))], 0)
            
            status_effect_report = status_effect.apply_effect(self_target)
            self_target.status_effects.append(status_effect)
            
            report['Status Effects'].append(status_effect_report)

            report['Attacks'].append(attack_method(target))

            return report

        super().__init__('Smite', False, effect, cooldown)

class TripleSlash(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=3):
        def effect(target, *args) -> dict[dict]:
            report = {'name': 'Triple Slash', 'Status Effects': [], 'Attacks': []}
            for _ in range(3):
                report['Attacks'].append(attack_method(target))

            return report
        
        super().__init__('Triple Slash', False, effect, cooldown)

class Distract(Skill):
    def __init__(self, cooldown=3):
        super().__init__('Distract', False, Distract.effect, cooldown)

    def effect(target, *args) -> dict:
        status_effect = StatusEffect('Distracted', [('defence', -10)], 0)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)

class Bless(Skill):
    def __init__(self, cooldown=5):
        super().__init__('Bless', True, Bless.effect, cooldown)

    def effect(target, *args):
        status_effect = StatusEffect('Blessed', [('attack', 2), ('damage_dice', Die(4))], 4)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)
        
class Heal(Skill):
    def __init__(self, cooldown=10):
        super().__init__('Heal', True, Heal.effect, cooldown)

    def effect(target, *args):
        amount = DiceGroup([Die(8), Die(8)]).roll()
        target.heal(amount)
        return {'name': 'Heal',
                'effects': [{'stat': 'health', 'value': amount}],
                'target': target.name
                }

class Agathys(Skill):
    def __init__(self, cooldown=20):
        super().__init__('Armour of Agathys', True, Agathys.effect, cooldown)

    def effect(target, *args):
        status_effect = StatusEffect('Armour of Agathys', [('temporary_health', 5), ('biteback', 5)], 5)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)
        
class InvincibleConqueror(Skill):
    def __init__(self, cooldown=100):
        super().__init__('Invincible Conqueror', True, InvincibleConqueror.effect, cooldown)

    def effect(target, *args):
        status_effect = StatusEffect('Invincible Conqueror', [('resistance', 1), ('attack_number', 1), ('crit_range', -1)], 10)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)

class ShieldOfFaith(Skill):
    def __init__(self, cooldown=40):
        super().__init__('Shield of Faith', True, ShieldOfFaith.effect, cooldown)

    def effect(target, *args):
        status_effect = StatusEffect('Shield of Faith', [('defence', 2)], 10)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)
      
class SacredWeapon(Skill):
    def __init__(self, cooldown=40):
        super().__init__('Sacred Weapon', True, SacredWeapon.effect, cooldown)

    def effect(target, *args):
        status_effect = StatusEffect('Sacred Weapon', [('damage_dice', Die(8))], 15)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)

class HolyNimbus(Skill):
    def __init__(self, cooldown=100):
        super().__init__('Holy Nimbus', True, HolyNimbus.effect, cooldown)

    def effect(target, *args):
        status_effect = StatusEffect('Holy Nimbus', [('defence', 2), ('armour', 2), ('passive_damage', 10)], 10)
        target.status_effects.append(status_effect)
        return status_effect.apply_effect(target)

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