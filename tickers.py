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

    def activate(self, target):
        print(self.name, 'was activated!', self.effect)
        self.effect(target)
        self.timer = self.cooldown



class StatusEffect(Ticker):
    def __init__(self, name, target, effects: list[tuple[str, int]], duration):
        super().__init__(duration)
        self.target = target
        self.name = name
        self.effects = effects
        self.apply_effect()
    
    
    def apply_effect(self):
        self.target.status_effects.append(self)
        print('[StatusEffect] applying', self.effects, 'to', self.target)
        for effect in self.effects:
            effect_stat, stat_change = effect
            if effect_stat == 'defence':
                self.target.defence += stat_change
            elif effect_stat == 'attack':
                self.target.attack += stat_change
            elif effect_stat == 'damage':
                self.target.damage += stat_change
            else:
                raise NotImplementedError(f"[apply_effect] {effect_stat} not implemented")

    def remove_effect(self):
        for effect in self.effects:
            effect_stat, stat_change = effect
            if effect_stat == 'defence':
                self.target.defence -= stat_change
            elif effect_stat == 'attack':
                self.target.attack -= stat_change
            elif effect_stat == 'damage':
                self.target.damage -= stat_change
            else:
                raise NotImplementedError(f"[apply_effect] {effect_stat} not implemented")

    def update(self):
        super().update()

    def  __eq__(self, value: str) -> bool:
        return self.name == value
    
    def __repr__(self) -> str:
        return f'StatusEffect(name={self.name}, turns_left={self.timer})'
