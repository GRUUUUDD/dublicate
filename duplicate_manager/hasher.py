"""
Модуль для вычисления хешей файлов (УР1: поиск одинаковых файлов)
"""

import hashlib
from pathlib import Path
from typing import Optional
from duplicate_manager.config import Config


class FileHasher:
    """Класс для вычисления хешей файлов"""
    
    def __init__(self, config: Config):
        """
        Инициализация
        
        Args:
            config: объект конфигурации
        """
        self.config = config
        self.algorithm = config.get("hash_algorithm", "md5")
        self.chunk_size = config.get("chunk_size", 8192)
    
    def calculate_hash(self, file_path: Path) -> Optional[str]:
        """
        Вычислить хеш файла
        
        Args:
            file_path: путь к файлу
            
        Returns:
            хеш файла в hex формате или None в случае ошибки
        """
        try:
            if self.algorithm == "md5":
                hasher = hashlib.md5()
            elif self.algorithm == "sha256":
                hasher = hashlib.sha256()
            else:
                raise ValueError(f"Неподдерживаемый алгоритм: {self.algorithm}")
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    hasher.update(chunk)
            
            return hasher.hexdigest()
        except (IOError, OSError) as e:
            print(f"Ошибка при вычислении хеша для {file_path}: {e}")
            return None
    
    def get_file_size(self, file_path: Path) -> int:
        """
        Получить размер файла
        
        Args:
            file_path: путь к файлу
            
        Returns:
            размер файла в байтах
        """
        try:
            return file_path.stat().st_size
        except (OSError, IOError):
            return 0
    
    def should_process(self, file_path: Path) -> bool:
        """
        Проверить, нужно ли обрабатывать файл
        
        Args:
            file_path: путь к файлу
            
        Returns:
            True если файл нужно обработать
        """
        if not file_path.is_file():
            return False
        
        if self.config.should_exclude(file_path):
            return False
        
        file_size = self.get_file_size(file_path)
        min_size = self.config.get("min_file_size", 0)
        max_size = self.config.get("max_file_size")
        
        if file_size < min_size:
            return False
        
        if max_size is not None and file_size > max_size:
            return False
        
        return True

