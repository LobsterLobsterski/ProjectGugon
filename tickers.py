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



class StatusEffect(Ticker):
    def __init__(self, name, effects: list[tuple[str, int]], duration):
        super().__init__(duration)
        self.name = name
        self.effects = effects
    
    def apply_effect(self, target):
        target.status_effects.append(self)
        print('[StatusEffect] applying', self.effects, 'to', target)
        for effect in self.effects:
            effect_stat, stat_change = effect
            target.attributes[effect_stat] += stat_change

    def remove_effect(self, target):
        for effect in self.effects:
            effect_stat, stat_change = effect
            target.attributes[effect_stat] -= stat_change

    def update(self):
        super().update()

    def  __eq__(self, value: str) -> bool:
        return self.name == value
    
    def __repr__(self) -> str:
        return f'StatusEffect(name={self.name}, turns_left={self.timer})'

class Distract(Skill):
    def __init__(self):
        super().__init__('Distract', False, Distract.effect, 3)

    def effect(target, *args):
        print('[Distract]:', target, args)
        s = StatusEffect('Distracted', [('defence', -10)], 1)
        s.apply_effect(target)

class Rampage(Skill):
    def __init__(self, attack_method: callable):
        def effect(target, self_target):
            s = StatusEffect('Out of Position', [('defence', -20)], 3)
            s.apply_effect(self_target)
            s = StatusEffect('Out of Position', [('attack', -15)], 1)
            s.apply_effect(self_target)

            for _ in range(3):
                attack_method(target)

        super().__init__('Rampage', True, effect, 5)

    