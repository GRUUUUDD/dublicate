"""
Модуль для индексации файлов для быстрого поиска
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from duplicate_manager.config import Config
from duplicate_manager.hasher import FileHasher


class FileIndex:
    """Класс для индексации файлов"""
    
    def __init__(self, config: Config):
        """
        Инициализация
        
        Args:
            config: объект конфигурации
        """
        self.config = config
        self.index_path = Path(config.get("index_path", ".duplicate_index"))
        self.index: Dict[str, Dict] = {}  # hash -> {files: [paths], size: int, modified: datetime}
        self.hasher = FileHasher(config)
        self.load()
    
    def load(self) -> None:
        """Загрузить индекс из файла"""
        if not self.index_path.exists():
            return
        
        try:
            # Пробуем загрузить как JSON
            with open(self.index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Преобразуем строки дат обратно в datetime
                for hash_val, info in data.items():
                    if 'modified' in info:
                        info['modified'] = datetime.fromisoformat(info['modified'])
                self.index = data
        except (json.JSONDecodeError, IOError):
            # Если не получилось, пробуем pickle
            try:
                with open(self.index_path, 'rb') as f:
                    self.index = pickle.load(f)
            except (pickle.UnpicklingError, IOError):
                self.index = {}
    
    def save(self) -> None:
        """Сохранить индекс в файл"""
        try:
            # Сохраняем как JSON для читаемости
            data = {}
            for hash_val, info in self.index.items():
                info_copy = info.copy()
                if 'modified' in info_copy and isinstance(info_copy['modified'], datetime):
                    info_copy['modified'] = info_copy['modified'].isoformat()
                data[hash_val] = info_copy
            
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Ошибка сохранения индекса: {e}")
    
    def add_file(self, file_path: Path) -> Optional[str]:
        """
        Добавить файл в индекс
        
        Args:
            file_path: путь к файлу
            
        Returns:
            хеш файла или None в случае ошибки
        """
        if not self.hasher.should_process(file_path):
            return None
        
        file_hash = self.hasher.calculate_hash(file_path)
        if file_hash is None:
            return None
        
        file_size = self.hasher.get_file_size(file_path)
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        if file_hash not in self.index:
            self.index[file_hash] = {
                'files': [],
                'size': file_size,
                'modified': modified_time
            }
        
        file_str = str(file_path.absolute())
        if file_str not in self.index[file_hash]['files']:
            self.index[file_hash]['files'].append(file_str)
        
        return file_hash
    
    def get_duplicates(self) -> Dict[str, List[str]]:
        """
        Получить все дубликаты из индекса
        
        Returns:
            словарь {hash: [список путей к файлам]}
        """
        duplicates = {}
        for file_hash, info in self.index.items():
            if len(info['files']) > 1:
                duplicates[file_hash] = info['files']
        return duplicates
    
    def find_file_hash(self, file_path: Path) -> Optional[str]:
        """
        Найти хеш файла в индексе (без пересчета)
        
        Args:
            file_path: путь к файлу
            
        Returns:
            хеш файла или None
        """
        file_str = str(file_path.absolute())
        for file_hash, info in self.index.items():
            if file_str in info['files']:
                return file_hash
        return None
    
    def remove_file(self, file_path: Path) -> None:
        """
        Удалить файл из индекса
        
        Args:
            file_path: путь к файлу
        """
        file_str = str(file_path.absolute())
        hashes_to_remove = []
        
        for file_hash, info in self.index.items():
            if file_str in info['files']:
                info['files'].remove(file_str)
                if not info['files']:
                    hashes_to_remove.append(file_hash)
        
        for file_hash in hashes_to_remove:
            del self.index[file_hash]
    
    def clear(self) -> None:
        """Очистить индекс"""
        self.index = {}
    
    def update_paths(self, old_path: Path, new_path: Path) -> None:
        """
        Обновить пути в индексе (например, при перемещении файлов)
        
        Args:
            old_path: старый путь
            new_path: новый путь
        """
        old_str = str(old_path.absolute())
        new_str = str(new_path.absolute())
        
        for file_hash, info in self.index.items():
            if old_str in info['files']:
                info['files'].remove(old_str)
                if new_str not in info['files']:
                    info['files'].append(new_str)

