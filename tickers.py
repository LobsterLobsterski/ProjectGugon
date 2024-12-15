import random

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

    def activate(self, target, self_target):
        print(self.name, 'was activated!', self.effect)
        self.effect(target, self_target)
        self.timer = self.cooldown
    
    def __repr__(self):
        return f'Skill({self.name})'

class AttackSkill(Skill):
    def __init__(self, name, target_is_self, effect, cooldown):
        super().__init__(name, target_is_self, effect, cooldown)


class StatusEffect(Ticker):
    def __init__(self, name, effects: list[tuple[str, int]], duration):
        super().__init__(duration)
        self.name = name
        self.effects = effects
        self.effect_values = []
    
    def apply_effect(self, target):
        target.status_effects.append(self)
        print('[StatusEffect] applying', self.effects, 'to', target)
        for effect in self.effects:
            effect_stat, stat_change = effect
            if isinstance(stat_change, str):
                dice_number, dice_size = stat_change.split('d')
                stat_change = sum([random.randint(1, int(dice_size)) for _ in range(int(dice_number))])

            self.effect_values.append(stat_change)
            target.attributes[effect_stat] += stat_change

    def remove_effect(self, target):
        for effect, effect_value in zip(self.effects, self.effect_values):
            effect_stat, _ = effect
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

    def effect(target, *args):
        StatusEffect('Distracted', [('defence', -10)], 0).apply_effect(target)

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
            StatusEffect('Smite', [('damage', '2d8')], 0).apply_effect(self_target)
            attack_method(target)

        super().__init__('Smite', False, effect, cooldown)

class Bless(Skill):
    def __init__(self, cooldown=5):
        super().__init__('Bless', True, Bless.effect, cooldown)

    def effect(target, *args):
        StatusEffect('Blessed', [('attack', 10), ('damage', 5)], 3).apply_effect(target)

class TripleSlash(AttackSkill):
    def __init__(self, attack_method: callable, cooldown=3):
        def effect(target, *args):
            for _ in range(3):
                print('TripleSlash target', target, args)
                attack_method(target)

        super().__init__('Triple Slash', False, effect, cooldown)


list_of_all_skills = [Distract, 
                      Rampage, 
                      Smite, 
                      Bless, 
                      TripleSlash
                    ]

def get_random_skills(number):
    return [random.choice(list_of_all_skills) for _ in range(number)]