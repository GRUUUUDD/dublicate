"""
Модуль для сканирования файловой системы
"""

from pathlib import Path
from typing import List, Set, Optional
from tqdm import tqdm
from duplicate_manager.config import Config
from duplicate_manager.indexer import FileIndex
from duplicate_manager.hasher import FileHasher
from duplicate_manager.text_matcher import TextMatcher
from duplicate_manager.image_matcher import ImageMatcher


class FileScanner:
    """Класс для сканирования файловой системы"""
    
    def __init__(self, config: Config):
        """
        Инициализация
        
        Args:
            config: объект конфигурации
        """
        self.config = config
        self.index = FileIndex(config)
        self.hasher = FileHasher(config)
        self.text_matcher = TextMatcher(config)
        self.image_matcher = ImageMatcher(config)
    
    def scan_directory(self, directory: Path, show_progress: bool = True) -> None:
        """
        Сканировать директорию и добавить файлы в индекс
        
        Args:
            directory: путь к директории
            show_progress: показывать ли прогресс-бар
        """
        if not directory.exists() or not directory.is_dir():
            print(f"Директория не существует: {directory}")
            return
        
        files = list(self._collect_files(directory))
        
        if show_progress:
            files_iter = tqdm(files, desc="Сканирование файлов")
        else:
            files_iter = files
        
        for file_path in files_iter:
            self.index.add_file(file_path)
        
        self.index.save()
        print(f"Проиндексировано файлов: {len(files)}")
    
    def _collect_files(self, directory: Path) -> List[Path]:
        """
        Собрать все файлы из директории
        
        Args:
            directory: путь к директории
            
        Returns:
            список путей к файлам
        """
        files = []
        
        try:
            for item in directory.rglob('*'):
                if item.is_file() and self.hasher.should_process(item):
                    files.append(item)
        except (PermissionError, OSError) as e:
            print(f"Ошибка доступа к {directory}: {e}")
        
        return files
    
    def find_exact_duplicates(self) -> dict:
        """
        Найти точные дубликаты (УР1)
        
        Returns:
            словарь {hash: [список путей]}
        """
        return self.index.get_duplicates()
    
    def find_text_containments(self) -> List[tuple]:
        """
        Найти вложенные текстовые файлы (УР2)
        
        Returns:
            список кортежей (контейнер, содержимое, коэффициент)
        """
        text_files = []
        
        # Собираем все текстовые файлы из индекса
        for file_hash, info in self.index.index.items():
            for file_path_str in info['files']:
                file_path = Path(file_path_str)
                if file_path.exists() and self.config.is_supported_text(file_path):
                    text_files.append(file_path)
        
        return self.text_matcher.find_all_containments(text_files)
    
    def find_image_duplicates(self) -> List[tuple]:
        """
        Найти дублирующиеся изображения (УР3)
        
        Returns:
            список кортежей (путь1, путь2, коэффициент схожести)
        """
        image_files = []
        
        # Собираем все изображения из индекса
        for file_hash, info in self.index.index.items():
            for file_path_str in info['files']:
                file_path = Path(file_path_str)
                if file_path.exists() and self.config.is_supported_image(file_path):
                    image_files.append(file_path)
        
        return self.image_matcher.find_all_duplicates(image_files)
    
    def get_statistics(self) -> dict:
        """
        Получить статистику по индексу
        
        Returns:
            словарь со статистикой
        """
        total_files = 0
        total_size = 0
        unique_files = 0
        duplicate_groups = 0
        
        for file_hash, info in self.index.index.items():
            file_count = len(info['files'])
            total_files += file_count
            total_size += info['size'] * file_count
            
            if file_count == 1:
                unique_files += 1
            else:
                duplicate_groups += 1
        
        return {
            'total_files': total_files,
            'unique_files': unique_files,
            'duplicate_groups': duplicate_groups,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'wasted_space_bytes': sum(
                (len(info['files']) - 1) * info['size']
                for info in self.index.index.values()
                if len(info['files']) > 1
            )
        }

