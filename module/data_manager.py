"""
Менеджер данных для сохранения и загрузки данных приложения
"""
import json
import os
from pathlib import Path

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "app_data.json"

def ensure_data_dir():
    """Создает папку data, если её нет"""
    DATA_DIR.mkdir(exist_ok=True)

def load_data():
    """Загружает данные из JSON файла"""
    ensure_data_dir()
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    # Возвращаем структуру по умолчанию
    return {
        "tasks": [],
        "habits": [],
        "theme": "light"
    }

def save_data(data):
    """Сохраняет данные в JSON файл"""
    ensure_data_dir()
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False
