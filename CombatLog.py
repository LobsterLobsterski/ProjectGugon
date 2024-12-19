import pygame as pg

from tickers import Skill

class CombatLog:
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
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def add_attack_message(self, attack_data: dict, target_name: str, color=None):
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
            hit_message = f'Player attacked {target_name} and {"critically" if is_crit else "" } hit! ({attack_roll}+{attack_bonus})!'
            if is_crit:
                hit_color = (102, 255, 0)
                damage_color = (102, 255, 0)

            damage_message = f'Player dealt {total} ({damage_roll}+{damage_bonus}-target_armour)!'
            if damage_received:
                damage_message = f'{damage_message} and received {damage_received} from biteback!'

            self.messages.append((hit_message, hit_color))
            self.messages.append((damage_message, damage_color))

        else:
            hit_color = (0, 0, 255)
            self.messages.append((f'Player attacked {target_name} and missed! ({attack_roll}+{attack_bonus})', hit_color))


        self.check_messages()

    def add_defend_message(self, user_name: str):
        self.messages.append((f'{user_name} defends!', self.color))
        self.check_messages()

    def add_skill_message(self, skill_report: dict, user_name: str, target_name=None):
        skill_name = skill_report['name']
        skill_effects = skill_report['effects']

        self.messages.append((f'{user_name} used {skill_name}!', self.color))
        for effect in skill_effects:
            stat = effect['stat'].replace('_', ' ').capitalize()
            value = effect['value']

            self.messages.append((f'{stat} increased by {value}!', self.color))

        self.check_messages()

    def add_escape_message(self, user_name: str):
        raise NotImplementedError('add_escape_message not implmented yet!')
        self.messages.append((f'{user_name} defends!', self.color))
        self.check_messages()
    
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
