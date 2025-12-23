"""
Модуль для поиска вложенных текстовых файлов (УР2: один файл содержит другой)
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional, Set
from duplicate_manager.config import Config


class TextMatcher:
    """Класс для поиска вложенных текстовых файлов"""
    
    def __init__(self, config: Config):
        """
        Инициализация
        
        Args:
            config: объект конфигурации
        """
        self.config = config
        self.threshold = config.get("text_containment_threshold", 0.8)
        self.chunk_size = config.get("chunk_size", 8192)
    
    def read_text_file(self, file_path: Path) -> Optional[str]:
        """
        Прочитать текстовый файл с автоматическим определением кодировки
        
        Args:
            file_path: путь к файлу
            
        Returns:
            содержимое файла или None в случае ошибки
        """
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1251', 'cp866']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, IOError):
                continue
        
        # Если не удалось прочитать как текст, попробуем бинарный режим
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # Попытка декодирования как UTF-8 с игнорированием ошибок
                return content.decode('utf-8', errors='ignore')
        except IOError:
            return None
    
    def normalize_text(self, text: str) -> str:
        """
        Нормализовать текст для сравнения
        
        Args:
            text: исходный текст
            
        Returns:
            нормализованный текст
        """
        # Удаление лишних пробелов и переводов строк
        text = re.sub(r'\s+', ' ', text)
        # Приведение к нижнему регистру
        text = text.lower()
        # Удаление знаков препинания (опционально)
        # text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    def calculate_containment(self, container_text: str, contained_text: str) -> float:
        """
        Вычислить степень содержания одного текста в другом
        
        Args:
            container_text: текст-контейнер
            contained_text: текст, который должен содержаться
            
        Returns:
            коэффициент содержания (0-1)
        """
        if not contained_text:
            return 0.0
        
        container_normalized = self.normalize_text(container_text)
        contained_normalized = self.normalize_text(contained_text)
        
        if not contained_normalized:
            return 0.0
        
        # Простой алгоритм: проверка вхождения
        if contained_normalized in container_normalized:
            return 1.0
        
        # Более сложный алгоритм: проверка по словам
        contained_words = set(contained_normalized.split())
        container_words = set(container_normalized.split())
        
        if not contained_words:
            return 0.0
        
        common_words = contained_words.intersection(container_words)
        return len(common_words) / len(contained_words)
    
    def find_contained_files(self, file_path: Path, other_files: List[Path]) -> List[Tuple[Path, float]]:
        """
        Найти файлы, которые содержатся в данном файле
        
        Args:
            file_path: путь к файлу-контейнеру
            other_files: список других файлов для проверки
            
        Returns:
            список кортежей (путь к файлу, коэффициент содержания)
        """
        container_text = self.read_text_file(file_path)
        if not container_text:
            return []
        
        results = []
        
        for other_file in other_files:
            if other_file == file_path:
                continue
            
            if not self.config.is_supported_text(other_file):
                continue
            
            contained_text = self.read_text_file(other_file)
            if not contained_text:
                continue
            
            containment = self.calculate_containment(container_text, contained_text)
            
            if containment >= self.threshold:
                results.append((other_file, containment))
        
        return results
    
    def find_all_containments(self, text_files: List[Path]) -> List[Tuple[Path, Path, float]]:
        """
        Найти все пары файлов, где один содержит другой
        
        Args:
            text_files: список текстовых файлов
            
        Returns:
            список кортежей (контейнер, содержимое, коэффициент)
        """
        results = []
        
        for i, file1 in enumerate(text_files):
            if not self.config.is_supported_text(file1):
                continue
            
            for file2 in text_files[i+1:]:
                if not self.config.is_supported_text(file2):
                    continue
                
                # Проверяем оба направления
                text1 = self.read_text_file(file1)
                text2 = self.read_text_file(file2)
                
                if not text1 or not text2:
                    continue
                
                # file1 содержит file2?
                containment1 = self.calculate_containment(text1, text2)
                if containment1 >= self.threshold:
                    results.append((file1, file2, containment1))
                
                # file2 содержит file1?
                containment2 = self.calculate_containment(text2, text1)
                if containment2 >= self.threshold:
                    results.append((file2, file1, containment2))
        
        return results

