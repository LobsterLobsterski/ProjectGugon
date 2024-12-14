from tickers import Distract, Rampage, Skill, StatusEffect


class ClassTable:
    def __init__(self, level=0):
        self.level = level
        self.level_features_dict = {
            1: ...,
            2: ...,
            3: ...,
            4: ...,
            5: ...,
            6: ...,
            7: ...,
            8: ...,
            9: ...,
            10: ...,
            11: ...,
            12: ...,
            13: ...,
            14: ...,
            15: ...,
            16: ...,
            17: ...,
            18: ...,
            19: ...,
            20: ...
        }

    def level_up(self):
        self.level+=1
        return self.level_features_dict[self.level]
    

class Paladin(ClassTable):
    def __init__(self, level=0):
        super().__init__(level)
        
    def init_attack_method(self, attack_method):
        self.level_features_dict = {
            1: [Skill('Bless', True,  lambda target, *args: StatusEffect('Blessed', [('attack', 10), ('damage', 5)], 3).apply_effect(target), 5), 
                Skill('Triple Slash', False, lambda target, *args: [attack_method(target) for _ in range(3)], 3)
                ],
            2: ['Fighting style', 'Smite'],
            3: ['Subclass'],
            4: ['Random card'],
            5: ['Double Attack', ('attack', 1)],
            6: ['Aura of Protection'],
            7: ['Subclass feature'],
            8: ['Random'],
            9: ['Random', ('attack', 1)],
            10: ['Aura of Courage'],
            11: ['Radiant strikes'],
            12: ['Random'],
            13: ['Random', ('attack', 1)],
            14: ['Nothing'],
            15: ['Heal'],
            16: ['Subclass feature'],
            17: ['Random', ('attack', 1)],
            18: ['Aura Master'],
            19: ['Epic Boon'],
            20: ['Subclass Feature']
        }

class SkeletonClass(ClassTable):
    def __init__(self, attack_method: callable, level=0):
        super().__init__(level)
        
        self.level_features_dict = {
                1: [Distract()
                    ,Rampage(attack_method)
                    ],
                2: ['Fighting style', 'Smite'],
                # 3: ['Subclass'],
                # 4: ['Random card'],
                # 5: ['Double Attack', ('attack', 1)],
                # 6: ['Aura of Protection'],
                # 7: ['Subclass feature'],
                # 8: ['Random'],
                # 9: ['Random', ('attack', 1)],
                # 10: ['Aura of Courage'],
                # 11: ['Radiant strikes'],
                # 12: ['Random'],
                # 13: ['Random', ('attack', 1)],
                # 14: ['Nothing'],
                # 15: ['Heal'],
                # 16: ['Subclass feature'],
                # 17: ['Random', ('attack', 1)],
                # 18: ['Aura Master'],
                # 19: ['Epic Boon'],
                # 20: ['Subclass Feature']
            }