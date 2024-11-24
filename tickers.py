class Ticker:
    def __init__(self, round_timer: int):
        self.timer = round_timer
    
    def is_ticking(self):
        return self.timer > 0
    
    def update(self):
        if self.is_ticking():
            self.timer-=1


class Skill(Ticker):
    def __init__(self, name, effect: callable, cooldown):
        super().__init__(0)
        self.name = name
        self.effect = effect
        self.cooldown = cooldown

    def activate(self):
        print(self.name, 'was activated!', self.effect)
        self.effect()
        self.timer = self.cooldown



class StatusEffect(Ticker):
    def __init__(self, name, effect: callable, duration):
        super().__init__(duration)
        self.name = name
        self.effect = effect
        self.apply()
    
    def apply(self):
        print('[StatusEffect] applying', self.effect)

    def  __eq__(self, value: str) -> bool:
        return self.name == value
    
    def __repr__(self) -> str:
        return f'StatusEffect(name={self.name}, turns_left={self.timer})'
