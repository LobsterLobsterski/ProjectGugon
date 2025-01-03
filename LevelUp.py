from math import inf
import random
from Dice import Die
from tickers import Agathys, AttackSkill, Bless, Distract, Heal, HolyNimbus, InvincibleConqueror, Rampage, SacredWeapon, ShieldOfFaith, Skill, Smite, StatusEffect, TripleSlash, get_epic_boons, get_random_skills


class ClassTable:
    def __init__(self, level=0):
        self.level = level
        self.experience_thresholds = [
            0, 300, 900, 2_700, 6_500, 
            14_000, 23_000, 34_000, 48_000, 64_000, 
            85_000, 100_000, 120_000, 140_000, 165_000, 
            195_000, 225_000, 265_000, 305_000, 355_000
            ]
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

    def next_experience_threshold(self) -> int | None:
        return self.experience_thresholds[self.level] if self.level<=20 else inf
    
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
          2: [StatusEffect('Aura of Conquest', [('passive_damage', self.level//2)], -1)],
          3: [StatusEffect('Scornful Rebuke', [('biteback', self.level//3)], -1)],
          4: [InvincibleConqueror()]
        }
        
class DevotionPaladin(ClassTable):
    def __init__(self, level=0):
        super().__init__(level)
        self.name = 'Paladin of Devotion'

        self.level_features_dict = {
          1: [ShieldOfFaith(), SacredWeapon()],
          2: [StatusEffect('Aura of Devotion', [('defence', 1), ('armour', 1), ('temporary_health', 10)], -1)], # temp: the temp hp needs to reapply at the start of battle
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
                2: [StatusEffect('Undeadly Vigour', [('regeneration', 2), ('armour', 2)], -1)],
                3: [TripleSlash(attack_method), Agathys()],
                4: [SacredWeapon('Necrotic Strikes')],
                5: [StatusEffect('Deadly Strikes', [('crit_range', -1)], -1), ('attack', 1)],
                6: [StatusEffect('Hardened bones', [('armour', 1)], -1), ('attack', 1), ('attack_number', 1)],
                7: [StatusEffect('Mastery over Weaponry', [('attack', 5)], -1)],
                8: [StatusEffect('Aura of Undeath', [('passive_damage', 3)], -1)],
                9: [('attack', 1)],
                10: [StatusEffect('Mighty Constitution', [('max_health', 20)], -1)],
                11: [random.choice(get_epic_boons())],
                12: [StatusEffect('Higher Undeadly Vigour', [('regeneration', 3)], -1)],
                13: [('attack', 2), ('damage', 5)],
                14: [StatusEffect('Magical Weaponry', [('damage_dice', Die(8))], -1)],
                15: [StatusEffect('Mightier Constitution', [('max_health', 40)], -1)],
                16: [StatusEffect('Deadlier Strikes', [('crit_range', -2)], -1)],
                17: [StatusEffect('Thorny carapace', [('biteback', 4)], -1)],
                18: [random.choice(get_epic_boons())],
                19: [('attack_number', 1)],
                20: [random.choice(get_epic_boons())]
            }