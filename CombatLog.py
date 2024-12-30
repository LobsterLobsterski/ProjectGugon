import pygame as pg

from Dice import DiceGroup, Die
from tickers import Skill

class CombatLog:
    LOG_LENGTH_LIMIT = 48
    def __init__(self, screen, rect, font=None, max_messages=10):
        """
        Initialize the CombatLog.

        :param screen: The pygame screen where the log will be drawn.
        :param rect: A pygame.Rect defining the position and size of the log window.
        :param font: A pygame.Font object for rendering text.
        :param max_messages: Maximum number of messages to keep in the log.
        """
        self.screen = screen
        self.rect = rect
        self.font = font if font else pg.font.Font(None, 18)
        self.max_messages = max_messages
        self.messages = []
        self.color = (255, 255, 255)

    def check_messages(self):
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def add_message(self, message: str, color: tuple[int, int, int]):
        if len(message) > self.LOG_LENGTH_LIMIT:
            words = message.split(' ')
            print('words', words)
            for _ in range(2):
                half_of_message = ''
                while len(half_of_message) < self.LOG_LENGTH_LIMIT and words:
                    half_of_message += words.pop(0)+' '

                self.messages.append((half_of_message, color))
            
        else:
            self.messages.append((message, color))

        self.check_messages()

    def add_attack_message(self, attack_data: dict, user_name:str, target_name: str, color=None):
        """
        Add a new message to the log.

        :param data: dict of data to base message on
        :param color: The color of the message text.
        """
        if color is None:
            color = self.color

        is_hit = attack_data['is_hit']
        is_crit = attack_data['is_crit']
        attack_roll = attack_data['roll']
        attack_bonus = attack_data['attack_bonus']

        damage_roll_info = attack_data['damage']
        damage_dealt = damage_roll_info['dealt']
        damage_roll = damage_dealt['damage_roll']
        damage_bonus = damage_dealt['damage_bonus']
        total = damage_dealt['total_received']

        damage_received = damage_roll_info['received']

        hit_color = (1, 150, 32)
        damage_color = color

        if is_hit:
            hit_message = f'{user_name} attacked {target_name} and {"critically" if is_crit else "" } hit! ({attack_roll}+{attack_bonus})!'
            if is_crit:
                hit_color = (102, 255, 0)
                damage_color = (102, 255, 0)

            damage_message = f'{user_name} dealt {total} ({damage_roll}+{damage_bonus}-target_armour)!'
            if damage_received:
                damage_message = f'{damage_message} and received {damage_received} from biteback!'

            self.add_message(hit_message, hit_color)
            self.add_message(damage_message, damage_color)

        else:
            hit_color = (120, 120, 255)
            self.add_message(f'{user_name} attacked {target_name} and missed! ({attack_roll}+{attack_bonus})', hit_color)

    def add_defend_message(self, user_name: str):
        self.add_message(f'{user_name} defends!', self.color)

    def add_status_effect_message(self, skill_report: dict, user_name: str, receiver_name: str, is_standalone_skill=True):
        skill_name = skill_report['name']
        skill_effects = skill_report['effects']

        if is_standalone_skill:
            self.add_message(f'{user_name} used {skill_name}!', self.color)
        
        for effect in skill_effects:
            stat = effect['stat'].replace('_', ' ').capitalize()
            value = effect['value']
            if isinstance(value, int):
                change_word = 'increased' if value > 0  else 'decreased'
                value = abs(value)
                
            elif isinstance(value, Die) or isinstance(value, DiceGroup):
                change_word = 'increased'
            
            self.add_message(f"{receiver_name}'s {stat} {change_word} by {value}!", self.color)

    def add_attack_skill_message(self, skill_reports: dict[dict], user_name: str, target_name: str):
            skill_name = skill_reports['name']
            status_effect_reports = skill_reports['Status Effects']
            attack_reports = skill_reports['Attacks']

            self.add_message(f'{user_name} used {skill_name} on {target_name}!', self.color)
            for status_effect_report in status_effect_reports:
                self.add_status_effect_message(status_effect_report, user_name, target_name, is_standalone_skill=False)

            for attack_report in attack_reports:
                self.add_attack_message(attack_report, user_name, target_name)
    
    def add_escape_message(self, user_name: str):
        self.add_message(f'{user_name} tries to escape!', self.color)

    def add_enemy_message(self, report: dict, enemy_name: str, target_name: str):
        if 'is_hit' in report:
            # normal attack
            self.add_attack_message(report, enemy_name, target_name)

        elif 'Status Effects' in report:
            # skill
            self.add_attack_skill_message(report, enemy_name, target_name)

        elif 'effects' in report:
            # status effect
            target_name = report['target']
            self.add_status_effect_message(report, enemy_name, target_name)

        else:
            raise NotImplementedError(f'{report.keys()}: such raport type is not implemented!')
                  
    def draw(self):
        """
        Draw the combat log onto the screen.
        """
        # Draw the log background
        pg.draw.rect(self.screen, (30, 30, 30), self.rect)
        pg.draw.rect(self.screen, (200, 200, 200), self.rect, 2)  # Border

        # Render messages, starting from the most recent
        y_offset = self.rect.y + 10
        for message, color in self.messages:
            text_surface = self.font.render(message, True, color)
            self.screen.blit(text_surface, (self.rect.x + 10, y_offset))
            y_offset += text_surface.get_height() + 5
