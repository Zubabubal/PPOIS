import json
from constants import DIFFICULTY_LEVELS

def load_high_scores():
    try:
        with open("high_scores.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {difficulty: 0 for difficulty in DIFFICULTY_LEVELS}

def save_high_scores(high_scores):
    try:
        with open("high_scores.json", "w") as f:
            json.dump(high_scores, f)
    except Exception as e:
        print(f"Ошибка сохранения рекордов: {e}")

HIGH_SCORES = load_high_scores()
