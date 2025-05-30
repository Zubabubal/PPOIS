# Настройки окна
WIDTH = 300
HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE  # 10
GRID_HEIGHT = HEIGHT // GRID_SIZE  # 20
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
