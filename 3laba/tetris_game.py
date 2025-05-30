import pygame
from menu import Menu
from sound_manager import SoundManager
from constants import WIDTH, HEIGHT, LIGHT_GRAY, BLACK, DARK_BLUE, WHITE, PREVIEW_X, PREVIEW_Y, PREVIEW_WIDTH, PREVIEW_HEIGHT, PREVIEW_SIZE, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, TEXT_BG, TEXT_SHADOW, YELLOW, RED
from utils import HIGH_SCORES

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH + 100, HEIGHT))
        pygame.display.set_caption("Тетрис")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("verdana", 16, bold=True)
        self.menu = Menu()
        self.state = None
        self.mode = "menu"
        self.fps = 60
        self.sound_manager = SoundManager()
        self.sound_manager.play_background()

    def draw_next_tetromino(self):
        pygame.draw.rect(self.screen, DARK_BLUE, (PREVIEW_X - 5, PREVIEW_Y - 5, PREVIEW_WIDTH + 10, PREVIEW_HEIGHT + 10))
        pygame.draw.rect(self.screen, WHITE, (PREVIEW_X - 5, PREVIEW_Y - 5, PREVIEW_WIDTH + 10, PREVIEW_HEIGHT + 10), 2)
        next_text = self.font.render("След.:", True, WHITE)
        next_shadow = self.font.render("След.:", True, TEXT_SHADOW)
        self.screen.blit(next_shadow, (PREVIEW_X, PREVIEW_Y - 20 + 2))
        self.screen.blit(next_text, (PREVIEW_X, PREVIEW_Y - 20))
        shape_width = len(self.state.next_tetromino.shape[0])
        shape_height = len(self.state.next_tetromino.shape)
        offset_x = (2 - shape_width) // 2 * PREVIEW_SIZE
        offset_y = (2 - shape_height) // 2 * PREVIEW_SIZE
        for y, row in enumerate(self.state.next_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        self.state.next_tetromino.color,
                        (PREVIEW_X + x * PREVIEW_SIZE + offset_x, PREVIEW_Y + y * PREVIEW_SIZE + offset_y, PREVIEW_SIZE - 1, PREVIEW_SIZE - 1)
                    )
                    pygame.draw.rect(
                        self.screen,
                        BLACK,
                        (PREVIEW_X + x * PREVIEW_SIZE + offset_x, PREVIEW_Y + y * PREVIEW_SIZE + offset_y, PREVIEW_SIZE - 1, PREVIEW_SIZE - 1),
                        1
                    )

    def draw_game(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, WIDTH, HEIGHT), 3)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.state.grid[y][x],
                                 (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))
                if self.state.grid[y][x] != BLACK:
                    pygame.draw.rect(self.screen, BLACK,
                                     (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1), 1)
        for y, row in enumerate(self.state.current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.state.current_tetromino.color,
                                     ((self.state.current_tetromino.x + x) * GRID_SIZE,
                                      (self.state.current_tetromino.y + y) * GRID_SIZE,
                                      GRID_SIZE - 1, GRID_SIZE - 1))
                    pygame.draw.rect(self.screen, BLACK,
                                     ((self.state.current_tetromino.x + x) * GRID_SIZE,
                                      (self.state.current_tetromino.y + y) * GRID_SIZE,
                                      GRID_SIZE - 1, GRID_SIZE - 1), 1)

        text_x = WIDTH + 10
        pygame.draw.rect(self.screen, TEXT_BG, (text_x - 10, 5, 95, 120))
        score_text = self.font.render("Счёт:", True, WHITE)
        score_value = self.font.render(f"{self.state.score}", True, WHITE)
        high_score_text = self.font.render("Рекорд:", True, WHITE)
        high_score_value = self.font.render(f"{HIGH_SCORES[self.state.difficulty]}", True, WHITE)
        level_text = self.font.render("Уровень:", True, WHITE)
        level_value = self.font.render(f"{self.state.level}", True, WHITE)
        score_shadow = self.font.render("Счёт:", True, TEXT_SHADOW)
        score_value_shadow = self.font.render(f"{self.state.score}", True, TEXT_SHADOW)
        high_score_shadow = self.font.render("Рекорд:", True, TEXT_SHADOW)
        high_score_value_shadow = self.font.render(f"{HIGH_SCORES[self.state.difficulty]}", True, TEXT_SHADOW)
        level_shadow = self.font.render("Уровень:", True, TEXT_SHADOW)
        level_value_shadow = self.font.render(f"{self.state.level}", True, TEXT_SHADOW)

        self.screen.blit(score_shadow, (text_x + 2, 12))
        self.screen.blit(score_text, (text_x, 10))
        self.screen.blit(score_value_shadow, (text_x + 2, 32))
        self.screen.blit(score_value, (text_x, 30))
        self.screen.blit(high_score_shadow, (text_x + 2, 52))
        self.screen.blit(high_score_text, (text_x, 50))
        self.screen.blit(high_score_value_shadow, (text_x + 2, 72))
        self.screen.blit(high_score_value, (text_x, 70))
        self.screen.blit(level_shadow, (text_x + 2, 92))
        self.screen.blit(level_text, (text_x, 90))
        self.screen.blit(level_value_shadow, (text_x + 2, 112))
        self.screen.blit(level_value, (text_x, 110))

        if self.state.paused:
            pause_text = self.font.render("Пауза (P)", True, YELLOW)
            pause_shadow = self.font.render("Пауза (P)", True, TEXT_SHADOW)
            pygame.draw.rect(self.screen, TEXT_BG, (
                WIDTH // 2 - pause_text.get_width() // 2 - 5, HEIGHT // 2 - 15, pause_text.get_width() + 10, 30))
            self.screen.blit(pause_shadow, (WIDTH // 2 - pause_text.get_width() // 2 + 2, HEIGHT // 2 + 2))
            self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        elif self.state.game_over:
            game_over_text = self.font.render("Игра окончена! (R)", True, RED)
            game_over_shadow = self.font.render("Игра окончена! (R)", True, TEXT_SHADOW)
            pygame.draw.rect(self.screen, TEXT_BG, (
                WIDTH // 2 - game_over_text.get_width() // 2 - 5, HEIGHT // 2 - 15, game_over_text.get_width() + 10, 30))
            self.screen.blit(game_over_shadow, (WIDTH // 2 - game_over_text.get_width() // 2 + 2, HEIGHT // 2 + 2))
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))

        pause_hint = self.font.render("P - пауза", True, WHITE)
        exit_hint = self.font.render("Q - выход", True, WHITE)
        pause_shadow = self.font.render("P - пауза", True, TEXT_SHADOW)
        exit_shadow = self.font.render("Q - выход", True, TEXT_SHADOW)
        hint_x = WIDTH + 10
        pygame.draw.rect(self.screen, TEXT_BG, (hint_x - 10, HEIGHT - 70, 95, 65))
        self.screen.blit(pause_shadow, (hint_x + 2, HEIGHT - 62))
        self.screen.blit(exit_shadow, (hint_x + 2, HEIGHT - 37))
        self.screen.blit(pause_hint, (hint_x, HEIGHT - 60))
        self.screen.blit(exit_hint, (hint_x, HEIGHT - 35))

        self.draw_next_tetromino()
