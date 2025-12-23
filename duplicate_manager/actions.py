"""
Модуль для действий с найденными дубликатами
"""

import shutil
from pathlib import Path
from typing import List, Tuple
from duplicate_manager.indexer import FileIndex


class FileActions:
    """Класс для выполнения действий с файлами"""
    
    def __init__(self, index: FileIndex):
        """
        Инициализация
        
        Args:
            index: объект индекса
        """
        self.index = index
    
    def delete_file(self, file_path: Path, update_index: bool = True) -> bool:
        """
        Удалить файл
        
        Args:
            file_path: путь к файлу
            update_index: обновить ли индекс после удаления
            
        Returns:
            True если успешно
        """
        try:
            if file_path.exists():
                file_path.unlink()
                if update_index:
                    self.index.remove_file(file_path)
                    self.index.save()
                return True
        except (OSError, IOError) as e:
            print(f"Ошибка удаления файла {file_path}: {e}")
            return False
        return False
    
    def move_file(self, source: Path, destination: Path, update_index: bool = True) -> bool:
        """
        Переместить файл
        
        Args:
            source: исходный путь
            destination: путь назначения
            update_index: обновить ли индекс после перемещения
            
        Returns:
            True если успешно
        """
        try:
            if source.exists():
                # Создаем директорию назначения если нужно
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.move(str(source), str(destination))
                
                if update_index:
                    self.index.update_paths(source, destination)
                    self.index.save()
                return True
        except (OSError, IOError, shutil.Error) as e:
            print(f"Ошибка перемещения файла {source} -> {destination}: {e}")
            return False
        return False
    
    def copy_file(self, source: Path, destination: Path) -> bool:
        """
        Копировать файл
        
        Args:
            source: исходный путь
            destination: путь назначения
            
        Returns:
            True если успешно
        """
        try:
            if source.exists():
                # Создаем директорию назначения если нужно
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(str(source), str(destination))
                return True
        except (OSError, IOError, shutil.Error) as e:
            print(f"Ошибка копирования файла {source} -> {destination}: {e}")
            return False
        return False
    
    def create_hard_link(self, source: Path, destination: Path) -> bool:
        """
        Создать жесткую ссылку (hard link) вместо дубликата
        
        Args:
            source: исходный файл
            destination: путь для ссылки
            
        Returns:
            True если успешно
        """
        try:
            if source.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                if destination.exists():
                    destination.unlink()
                
                destination.hardlink_to(source)
                return True
        except (OSError, IOError) as e:
            print(f"Ошибка создания жесткой ссылки {source} -> {destination}: {e}")
            return False
        return False
    
    def delete_duplicates_keep_one(self, duplicate_group: List[str], keep_index: int = 0) -> int:
        """
        Удалить дубликаты, оставив один файл
        
        Args:
            duplicate_group: список путей к дубликатам
            keep_index: индекс файла, который нужно оставить
            
        Returns:
            количество удаленных файлов
        """
        if keep_index >= len(duplicate_group):
            keep_index = 0
        
        kept_file = Path(duplicate_group[keep_index])
        deleted_count = 0
        
        for i, file_path_str in enumerate(duplicate_group):
            if i == keep_index:
                continue
            
            file_path = Path(file_path_str)
            if self.delete_file(file_path):
                deleted_count += 1
        
        return deleted_count
    
    def move_duplicates_to_folder(self, duplicate_group: List[str], target_folder: Path, keep_index: int = 0) -> int:
        """
        Переместить дубликаты в отдельную папку, оставив один на месте
        
        Args:
            duplicate_group: список путей к дубликатам
            target_folder: папка для перемещения
            keep_index: индекс файла, который нужно оставить на месте
            
        Returns:
            количество перемещенных файлов
        """
        if keep_index >= len(duplicate_group):
            keep_index = 0
        
        moved_count = 0
        
        for i, file_path_str in enumerate(duplicate_group):
            if i == keep_index:
                continue
            
            file_path = Path(file_path_str)
            destination = target_folder / file_path.name
            
            # Если файл с таким именем уже существует, добавляем суффикс
            counter = 1
            while destination.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                destination = target_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            if self.move_file(file_path, destination):
                moved_count += 1
        
        return moved_count

