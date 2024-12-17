from Dice import Die
from tickers import Agathys, AttackSkill, Bless, Distract, Heal, HolyNimbus, InvincibleConqueror, Rampage, SacredWeapon, ShieldOfFaith, Skill, Smite, StatusEffect, TripleSlash, get_epic_boons, get_random_skills


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
        if self.level <= max(self.level_features_dict.keys()):
            return self.level_features_dict[self.level]
        
        print('maxed out level')
        return []
    
class Paladin(ClassTable):
    def __init__(self, level=0):
        super().__init__(level)
        self.subclass = ClassTable()

    def subclass_levelup(self) -> list:
        return self.subclass.level_up()

    def init_attack_method(self, attack_method: callable):
        # NOTE: for later, you can only have one aura active at any one time unless you have aura master which allows
        # using as many auras as you want
        self.level_features_dict = {
            1: [
                    Bless(), 
                    TripleSlash(attack_method)
                ],
            2: [[
                    StatusEffect('Defensive Fighter', [('defence', 1)], -1), 
                    StatusEffect('Duelist', [('damage', 2)], -1), 
                    StatusEffect('Great Weapon Fighter', [('attack', 2)], -1)
                ],
                    Smite(attack_method)],
            4: [[
                    ConquestPaladin(),
                    DevotionPaladin(),
                ]
                ],
            3: [
                    [skill() if not issubclass(skill, AttackSkill) else skill(attack_method) for skill in get_random_skills(3)]
               ],
            5: [
                    ('attack_number', 1),
                    ('attack', 1)
                ],
            6: [
                    StatusEffect('Aura of Protection', [('armour', 2)], -1)
                ],
            7: [
                    'subclass_levelup'
                ],
            8: [
                    [skill() if not issubclass(skill, AttackSkill) else skill(attack_method) for skill in get_random_skills(4)]
               ],
            9: [
                    [skill() if not issubclass(skill, AttackSkill) else skill(attack_method) for skill in get_random_skills(5)],
                    ('attack', 1)
                ],
            10: [
                    StatusEffect('Aura of Courage', [('attack', 2), ('damage_dice', Die(4))], -1)
                ],
            11: [
                    StatusEffect('Radiant Strikes', [('damage_dice', Die(8))], -1)
                ],
            12: [
                    [skill() if not issubclass(skill, AttackSkill) else skill(attack_method) for skill in get_random_skills(5)]
               ],
            13: [
                    [skill() if not issubclass(skill, AttackSkill) else skill(attack_method) for skill in get_random_skills(6)], 
                    ('attack', 1)
                ],
            14: [],
            15: [
                    Heal()
                ],
            16: [
                    'subclass_levelup'
                ],
            17: [
                    [skill() if not issubclass(skill, AttackSkill) else skill(attack_method) for skill in get_random_skills(6)], 
                    ('attack', 1)
                ],
            18: [
                    StatusEffect('Aura Master', 
                                 lambda passive_skills, *args: [aura for aura in passive_skills if 'Aura' in aura.name and setattr(aura, 'effects', [(effect[0], effect[1] + 2) for effect in aura.effects])], 
                                 -1)
                ], # NOTE: buff previous auras <- needs to be tested
            19: [
                    [get_epic_boons()]
                ],
            20: [
                    'subclass_levelup'
                ]
        }

class ConquestPaladin(ClassTable):
    def __init__(self, level=0):
        super().__init__(level)
        self.name = 'Paladin of Conquest'

        self.level_features_dict = {
          1: [Agathys()],
          2: [StatusEffect('Aura of Conquest', [('damage', self.level//2)], -1)], # this needs a new attribute ('passive damage') as it deals damage to all enemies
          3: [StatusEffect('Scornful Rebuke', [('damage', self.level//3)], -1)], # this needs a new attribute ('biteback') as it deals damage upon receiving damage
          4: [InvincibleConqueror()]
        }
        
class DevotionPaladin(ClassTable):
    def __init__(self, level=0):
        super().__init__(level)
        self.name = 'Paladin of Devotion'

        self.level_features_dict = {
          1: [ShieldOfFaith(), SacredWeapon()],
          2: [StatusEffect('Aura of Devotion', [('defence', 1), ('armour', 1), ('health', 5)], -1)], # temp: health needs to become temporary_health
          3: [StatusEffect('Smite of Protection', [('defence', 1), ('armour', 1)], -1)], # temp: needs to buff smite to also give defence +2 when used for 5 turns
          4: [HolyNimbus()]
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