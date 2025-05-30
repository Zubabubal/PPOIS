from tetromino import Tetromino
from constants import BLACK, GRID_WIDTH, GRID_HEIGHT, DIFFICULTY_LEVELS
from utils import HIGH_SCORES, save_high_scores

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
                    HIGH_SCORES[self.difficulty] = max(HIGH_SCORES[self.difficulty], self.score)
                    save_high_scores(HIGH_SCORES)
                return cleared_lines
        return 0
