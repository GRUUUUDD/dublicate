"""
Модуль конфигурации для параметризации поиска
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any


class Config:
    """Класс для управления конфигурацией"""
    
    DEFAULT_CONFIG = {
        "hash_algorithm": "md5",  # md5 или sha256
        "min_file_size": 0,  # минимальный размер файла в байтах
        "max_file_size": None,  # максимальный размер файла в байтах (None = без ограничений)
        "exclude_patterns": [".git", "__pycache__", "node_modules", ".venv", "venv"],
        "exclude_extensions": [".tmp", ".swp", ".DS_Store"],
        "image_similarity_threshold": 0.95,  # порог схожести изображений (0-1)
        "text_containment_threshold": 0.8,  # порог содержания текста (0-1)
        "index_path": ".duplicate_index",  # путь к файлу индекса
        "chunk_size": 8192,  # размер чанка для чтения файлов
        "supported_image_formats": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"],
        "supported_text_extensions": [".txt", ".py", ".js", ".html", ".css", ".md", ".json", ".xml", ".csv"],
        "removable_drives": [],  # список путей к съемным носителям
        "cloud_paths": [],  # список путей к облачным хранилищам
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация конфигурации
        
        Args:
            config_path: путь к файлу конфигурации (по умолчанию config.json в корне проекта)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"
        
        self.config_path = Path(config_path)
        self.config = self.DEFAULT_CONFIG.copy()
        
        if self.config_path.exists():
            self.load()
        else:
            self.save()
    
    def load(self) -> None:
        """Загрузка конфигурации из файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки конфигурации: {e}. Используются значения по умолчанию.")
    
    def save(self) -> None:
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Установить значение конфигурации"""
        self.config[key] = value
    
    def should_exclude(self, file_path: Path) -> bool:
        """
        Проверить, нужно ли исключить файл из поиска
        
        Args:
            file_path: путь к файлу
            
        Returns:
            True если файл нужно исключить
        """
        # Проверка расширения
        if file_path.suffix.lower() in self.config.get("exclude_extensions", []):
            return True
        
        # Проверка паттернов
        path_str = str(file_path)
        for pattern in self.config.get("exclude_patterns", []):
            if pattern in path_str:
                return True
        
        return False
    
    def is_supported_image(self, file_path: Path) -> bool:
        """Проверить, является ли файл поддерживаемым изображением"""
        return file_path.suffix.lower() in self.config.get("supported_image_formats", [])
    
    def is_supported_text(self, file_path: Path) -> bool:
        """Проверить, является ли файл поддерживаемым текстовым файлом"""
        return file_path.suffix.lower() in self.config.get("supported_text_extensions", [])

