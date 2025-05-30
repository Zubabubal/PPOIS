import pygame
from constants import BLACK, WHITE, YELLOW, TEXT_SHADOW, DIFFICULTY_LEVELS, WIDTH, HEIGHT
from utils import HIGH_SCORES

class Menu:
    def __init__(self):
        self.font = pygame.font.SysFont("verdana", 32, bold=True)
        self.hint_font = pygame.font.SysFont("verdana", 16)
        self.options = list(DIFFICULTY_LEVELS.keys())
        self.selected = 0
        self.mode = "main"

    def draw(self, screen):
        screen.fill(BLACK)
        total_height = 32 + 40 * len(self.options) + 20
        start_y = (HEIGHT - total_height) // 2 - 50
        if self.mode == "main":
            title = self.font.render("Тетрис", True, WHITE)
            title_shadow = self.font.render("Тетрис", True, TEXT_SHADOW)
            title_x = (WIDTH + 100) // 2 - title.get_width() // 2
            screen.blit(title_shadow, (title_x + 2, start_y + 2))
            screen.blit(title, (title_x, start_y))
            for i, option in enumerate(self.options):
                color = YELLOW if i == self.selected else WHITE
                text = self.font.render(option, True, color)
                text_shadow = self.font.render(option, True, TEXT_SHADOW)
                text_x = (WIDTH + 100) // 2 - text.get_width() // 2
                screen.blit(text_shadow, (text_x + 2, start_y + 50 + i * 40 + 2))
                screen.blit(text, (text_x, start_y + 50 + i * 40))
            hint = self.hint_font.render("Нажмите H для рекордов", True, WHITE)
            hint_x = (WIDTH + 100) // 2 - hint.get_width() // 2
            screen.blit(hint, (hint_x, start_y + 50 + len(self.options) * 40 + 20))
        elif self.mode == "high_scores":
            title = self.font.render("Рекорды", True, WHITE)
            title_shadow = self.font.render("Рекорды", True, TEXT_SHADOW)
            title_x = (WIDTH + 100) // 2 - title.get_width() // 2
            screen.blit(title_shadow, (title_x + 2, start_y + 2))
            screen.blit(title, (title_x, start_y))
            for i, (difficulty, score) in enumerate(HIGH_SCORES.items()):
                text = self.font.render(f"{difficulty}: {score}", True, WHITE)
                text_shadow = self.font.render(f"{difficulty}: {score}", True, TEXT_SHADOW)
                text_x = (WIDTH + 100) // 2 - text.get_width() // 2
                screen.blit(text_shadow, (text_x + 2, start_y + 50 + i * 40 + 2))
                screen.blit(text, (text_x, start_y + 50 + i * 40))
            hint = self.hint_font.render("Нажмите M для меню", True, WHITE)
            hint_x = (WIDTH + 100) // 2 - hint.get_width() // 2
            screen.blit(hint, (hint_x, start_y + 50 + len(self.options) * 40 + 20))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.mode == "main":
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected]
                elif event.key == pygame.K_h:
                    self.mode = "high_scores"
            elif self.mode == "high_scores":
                if event.key == pygame.K_m:
                    self.mode = "main"
        return None
