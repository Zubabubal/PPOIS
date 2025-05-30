import pygame
import random
import asyncio
import platform
import json
import os

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

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

# Хранилище рекордов
HIGH_SCORES = {difficulty: 0 for difficulty in DIFFICULTY_LEVELS}

# Функции для работы с рекордами
def export_high_scores():
    try:
        return json.dumps(HIGH_SCORES)
    except Exception as e:
        print(f"Ошибка при экспорте рекордов: {e}")
        return "{}"

def import_high_scores(json_str):
    global HIGH_SCORES
    try:
        loaded_scores = json.loads(json_str)
        # Проверка, что все ожидаемые ключи присутствуют
        expected_keys = set(DIFFICULTY_LEVELS.keys())
        if not isinstance(loaded_scores, dict) or not expected_keys.issubset(loaded_scores.keys()):
            print(f"Ошибка: HIGH_SCORES_JSON не содержит ожидаемые ключи {expected_keys}")
            return
        for key, value in loaded_scores.items():
            if key in HIGH_SCORES and isinstance(value, (int, float)):
                HIGH_SCORES[key] = int(value)
        print("Рекорды загружены из HIGH_SCORES_JSON:", HIGH_SCORES)
    except json.JSONDecodeError:
        print("Ошибка: Неверный формат HIGH_SCORES_JSON, используются рекорды по умолчанию")
    except Exception as e:
        print(f"Ошибка при загрузке HIGH_SCORES_JSON: {e}")

def save_high_scores_to_file():
    if platform.system() != "Emscripten":
        try:
            with open("high_scores.json", "w", encoding="utf-8") as f:
                json.dump(HIGH_SCORES, f)
            print("Рекорды сохранены в high_scores.json")
        except Exception as e:
            print(f"Ошибка при сохранении рекордов в файл: {e}")
    else:
        json_str = export_high_scores()
        print("Для сохранения рекордов в Pyodide скопируйте эту строку и вставьте в HIGH_SCORES_JSON в коде:")
        print(json_str)

def load_high_scores_from_file():
    if platform.system() != "Emscripten" and os.path.exists("high_scores.json"):
        try:
            with open("high_scores.json", "r", encoding="utf-8") as f:
                global HIGH_SCORES
                loaded_scores = json.load(f)
                for key, value in loaded_scores.items():
                    if key in HIGH_SCORES and isinstance(value, (int, float)):
                        HIGH_SCORES[key] = int(value)
            print("Рекорды загружены из high_scores.json:", HIGH_SCORES)
        except Exception as e:
            print(f"Ошибка при загрузке рекордов из файла: {e}")

# Загрузка рекордов при старте
HIGH_SCORES_JSON = '{"Лёгкий": 200, "Средний": 400, "Сложный": 600}'  # Замените на свои рекорды
if platform.system() == "Emscripten":
    import_high_scores(HIGH_SCORES_JSON)
else:
    load_high_scores_from_file()

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
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
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
            return
        self.fall_time += 1
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            if not self.check_collision(dy=1):
                self.current_tetromino.move(0, 1)
            else:
                self.merge()
                self.clear_lines()
                self.current_tetromino = Tetromino()
                if self.check_collision():
                    self.game_over = True
                    global HIGH_SCORES
                    HIGH_SCORES[self.difficulty] = max(HIGH_SCORES[self.difficulty], self.score)

class Menu:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 36)
        self.hint_font = pygame.font.SysFont("arial", 24)
        self.options = list(DIFFICULTY_LEVELS.keys())
        self.selected = 0
        self.mode = "main"

    def draw(self, screen):
        screen.fill(BLACK)
        if self.mode == "main":
            title = self.font.render("Тетрис", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            for i, option in enumerate(self.options):
                color = YELLOW if i == self.selected else WHITE
                text = self.font.render(option, True, color)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))
            hint = self.hint_font.render("Нажмите H для рекордов", True, WHITE)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))
        elif self.mode == "high_scores":
            title = self.font.render("Рекорды", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            for i, (difficulty, score) in enumerate(HIGH_SCORES.items()):
                text = self.font.render(f"{difficulty}: {score}", True, WHITE)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))
            hint = self.hint_font.render("Нажмите M для меню", True, WHITE)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 50))

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

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Тетрис")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.menu = Menu()
        self.state = None
        self.mode = "menu"
        self.fps = 60

    def draw_game(self):
        self.screen.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, self.state.grid[y][x],
                                 (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1))
        for y, row in enumerate(self.state.current_tetromino.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.state.current_tetromino.color,
                                     ((self.state.current_tetromino.x + x) * GRID_SIZE,
                                      (self.state.current_tetromino.y + y) * GRID_SIZE,
                                      GRID_SIZE - 1, GRID_SIZE - 1))
        score_text = self.font.render(f"Счёт: {self.state.score}", True, WHITE)
        high_score_text = self.font.render(f"Рекорд: {HIGH_SCORES[self.state.difficulty]}", True, WHITE)
        level_text = self.font.render(f"Уровень: {self.state.level}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))
        self.screen.blit(level_text, (10, 70))
        if self.state.paused:
            pause_text = self.font.render("Пауза (P)", True, YELLOW)
            self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        elif self.state.game_over:
            game_over_text = self.font.render("Игра окончена! Нажмите R", True, RED)
            self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
        hint_text = self.font.render("Q для выхода", True, WHITE)
        self.screen.blit(hint_text, (10, HEIGHT - 30))

    async def main(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_high_scores_to_file()
                    running = False
                elif self.mode == "menu":
                    selected_difficulty = self.menu.handle_input(event)
                    if selected_difficulty:
                        self.state = GameState(selected_difficulty)
                        self.mode = "game"
                elif self.mode == "game":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.state.paused = not self.state.paused
                        elif event.key == pygame.K_q:
                            save_high_scores_to_file()
                            running = False
                        elif not self.state.paused and not self.state.game_over:
                            if event.key == pygame.K_LEFT and not self.state.check_collision(dx=-1):
                                self.state.current_tetromino.move(-1, 0)
                            elif event.key == pygame.K_RIGHT and not self.state.check_collision(dx=1):
                                self.state.current_tetromino.move(1, 0)
                            elif event.key == pygame.K_DOWN and not self.state.check_collision(dy=1):
                                self.state.current_tetromino.move(0, 1)
                            elif event.key == pygame.K_UP:
                                original_shape = self.state.current_tetromino.shape
                                self.state.current_tetromino.rotate()
                                if self.state.check_collision():
                                    self.state.current_tetromino.shape = original_shape
                            elif event.key == pygame.K_SPACE:
                                while not self.state.check_collision(dy=1):
                                    self.state.current_tetromino.move(0, 1)
                                self.state.merge()
                                self.state.clear_lines()
                                self.state.current_tetromino = Tetromino()
                                if self.state.check_collision():
                                    self.state.game_over = True
                        elif self.state.game_over and event.key == pygame.K_r:
                            self.mode = "menu"

            if self.mode == "menu":
                self.menu.draw(self.screen)
            elif self.mode == "game" and self.state:
                self.state.update()
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(self.fps)
            await asyncio.sleep(1.0 / self.fps)

        pygame.quit()

if platform.system() == "Emscripten":
    game = TetrisGame()
    asyncio.ensure_future(game.main())
else:
    if __name__ == "__main__":
        game = TetrisGame()
        asyncio.run(game.main())