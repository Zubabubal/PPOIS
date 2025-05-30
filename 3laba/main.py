import pygame
import random
import asyncio
import os
import json

# Инициализация Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048)  # Моно

# Настройки окна
WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
PREVIEW_SIZE = 15
PREVIEW_X = WIDTH + 20
PREVIEW_Y = 150
PREVIEW_WIDTH = 2 * PREVIEW_SIZE
PREVIEW_HEIGHT = 2 * PREVIEW_SIZE

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
DARK_BLUE = (20, 20, 50)
LIGHT_GRAY = (100, 100, 100)
TEXT_BG = (40, 40, 40)
TEXT_SHADOW = (20, 20, 20)

# Формы тетромино
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # L
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1, 1]],          # I
    [[1, 1], [1, 1]],        # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1], [0, 1, 0]]   # T
]
SHAPE_COLORS = [CYAN, BLUE, RED, YELLOW, GREEN, MAGENTA, ORANGE]

# Уровни сложности
DIFFICULTY_LEVELS = {
    "Лёгкий": 30,
    "Средний": 20,
    "Сложный": 10
}

# Загрузка рекордов из файла
def load_high_scores():
    try:
        with open("high_scores.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {difficulty: 0 for difficulty in DIFFICULTY_LEVELS}

# Сохранение рекордов в файл
def save_high_scores(high_scores):
    try:
        with open("high_scores.json", "w") as f:
            json.dump(high_scores, f)
    except Exception as e:
        print(f"Ошибка сохранения рекордов: {e}")

# Инициализация рекордов
HIGH_SCORES = load_high_scores()

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = SHAPE_COLORS[SHAPES.index(self.shape)]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self):
        self.shape = list(zip(*reversed(self.shape)))

class GameState:
    def __init__(self, difficulty="Средний"):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_tetromino = Tetromino()
        self.next_tetromino = Tetromino()
        self.game_over = False
        self.score = 0
        self.difficulty = difficulty
        self.fall_time = 0
        self.fall_speed = DIFFICULTY_LEVELS.get(difficulty, 20)
        self.level = list(DIFFICULTY_LEVELS.keys()).index(difficulty) + 1
        self.paused = False

    def check_collision(self, dx=0, dy=0):
        for y, row in enumerate(self.current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_tetromino.x + x + dx
                    new_y = self.current_tetromino.y + y + dy
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                        return True
                    if self.grid[new_y][new_x] != BLACK:
                        return True
        return False

    def merge(self):
        for y, row in enumerate(self.current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_tetromino.y + y][self.current_tetromino.x + x] = self.current_tetromino.color

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == BLACK for cell in row)]
        cleared_lines = GRID_HEIGHT - len(new_grid)
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(cleared_lines)] + new_grid
        self.score += cleared_lines * 100 * self.level
        return cleared_lines

    def update(self):
        if self.paused or self.game_over:
            return 0
        self.fall_time += 1
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.check_collision(dy=1):
                self.current_tetromino.move(0, 1)
            else:
                self.merge()
                cleared_lines = self.clear_lines()
                self.current_tetromino = self.next_tetromino
                self.next_tetromino = Tetromino()
                if self.check_collision():
                    self.game_over = True
                    global HIGH_SCORES
                    HIGH_SCORES[self.difficulty] = max(HIGH_SCORES[self.difficulty], self.score)
                    save_high_scores(HIGH_SCORES)
                return cleared_lines
        return 0

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

class SoundManager:
    def __init__(self):
        pygame.mixer.set_num_channels(16)
        self.sounds = {}
        sound_path = "sounds"
        try:
            self.sounds = {
                'rotate': pygame.mixer.Sound(os.path.join(sound_path, 'rotate.wav')),
                'move': pygame.mixer.Sound(os.path.join(sound_path, 'move.wav')),
                'drop': pygame.mixer.Sound(os.path.join(sound_path, 'drop.wav')),
                'line_clear': pygame.mixer.Sound(os.path.join(sound_path, 'line_clear.wav')),
                'game_over': pygame.mixer.Sound(os.path.join(sound_path, 'game_over.wav')),
                'background': pygame.mixer.Sound(os.path.join(sound_path, 'background.wav'))
            }
            self.sounds['rotate'].set_volume(1.0)
            self.sounds['move'].set_volume(1.0)
            self.sounds['drop'].set_volume(1.0)
            self.sounds['line_clear'].set_volume(1.0)
            self.sounds['game_over'].set_volume(1.0)
            self.sounds['background'].set_volume(0.5)
        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")
            self.sounds = {
                'rotate': None,
                'move': None,
                'drop': None,
                'line_clear': None,
                'game_over': None,
                'background': None
            }
        self.background_playing = False

    def play(self, sound_name, loops=0):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play(loops=loops)
            except Exception as e:
                print(f"Ошибка воспроизведения звука {sound_name}: {e}")

    def stop(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].stop()
            except Exception as e:
                print(f"Ошибка остановки звука {sound_name}: {e}")

    def play_background(self):
        if not self.background_playing and self.sounds.get('background'):
            try:
                self.sounds['background'].play(loops=-1)
                self.background_playing = True
            except Exception as e:
                print(f"Ошибка воспроизведения фоновой музыки: {e}")

    def stop_background(self):
        if self.background_playing and self.sounds.get('background'):
            try:
                self.sounds['background'].stop()
                self.background_playing = False
            except Exception as e:
                print(f"Ошибка остановки фоновой музыки: {e}")

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

async def main():
    game = TetrisGame()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.sound_manager.stop_background()
                pygame.quit()
                return
            elif game.mode == "menu":
                if selected_difficulty := game.menu.handle_input(event):
                    game.state = GameState(selected_difficulty)
                    game.mode = "game"
                    game.sound_manager.play_background()
            elif game.mode == "game":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game.state.paused = not game.state.paused
                        if game.state.paused:
                            game.sound_manager.stop_background()
                        else:
                            game.sound_manager.play_background()
                    elif event.key == pygame.K_q:
                        game.sound_manager.stop_background()
                        pygame.quit()
                        return
                    elif not game.state.paused and not game.state.game_over:
                        if event.key == pygame.K_LEFT and not game.state.check_collision(dx=-1):
                            game.state.current_tetromino.move(-1, 0)
                            game.sound_manager.play('move')
                        elif event.key == pygame.K_RIGHT and not game.state.check_collision(dx=1):
                            game.state.current_tetromino.move(1, 0)
                            game.sound_manager.play('move')
                        elif event.key == pygame.K_DOWN and not game.state.check_collision(dy=1):
                            game.state.current_tetromino.move(0, 1)
                            game.sound_manager.play('move')
                        elif event.key == pygame.K_UP:
                            original_shape = game.state.current_tetromino.shape
                            game.state.current_tetromino.rotate()
                            if game.state.check_collision():
                                game.state.current_tetromino.shape = original_shape
                            else:
                                game.sound_manager.play('rotate')
                        elif event.key == pygame.K_SPACE:
                            while not game.state.check_collision(dy=1):
                                game.state.current_tetromino.move(0, 1)
                            game.sound_manager.play('drop')
                            game.state.merge()
                            if game.state.clear_lines() > 0:
                                game.sound_manager.play('line_clear')
                            game.state.current_tetromino = game.state.next_tetromino
                            game.state.next_tetromino = Tetromino()
                            if game.state.check_collision():
                                game.state.game_over = True
                                game.sound_manager.play('game_over')
                    elif game.state.game_over and event.key == pygame.K_r:
                        game.mode = "menu"
                        game.sound_manager.play_background()

        if game.mode == "menu":
            game.menu.draw(game.screen)
        elif game.mode == "game" and game.state:
            cleared_lines = game.state.update()
            if cleared_lines > 0:
                game.sound_manager.play('line_clear')
            game.draw_game()

        pygame.display.flip()
        game.clock.tick(game.fps)
        await asyncio.sleep(1.0 / game.fps)

if __name__ == "__main__":
    asyncio.run(main())
