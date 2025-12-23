"""
Модуль для сравнения изображений (УР3: картинки по содержанию, разные форматы)
"""

from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image
import imagehash
from duplicate_manager.config import Config


class ImageMatcher:
    """Класс для сравнения изображений"""
    
    def __init__(self, config: Config):
        """
        Инициализация
        
        Args:
            config: объект конфигурации
        """
        self.config = config
        self.threshold = config.get("image_similarity_threshold", 0.95)
    
    def load_image(self, file_path: Path) -> Optional[Image.Image]:
        """
        Загрузить изображение
        
        Args:
            file_path: путь к файлу изображения
            
        Returns:
            объект PIL Image или None в случае ошибки
        """
        try:
            return Image.open(file_path)
        except (IOError, OSError, Exception) as e:
            print(f"Ошибка загрузки изображения {file_path}: {e}")
            return None
    
    def calculate_image_hash(self, image: Image.Image) -> Optional[imagehash.ImageHash]:
        """
        Вычислить хеш изображения
        
        Args:
            image: объект PIL Image
            
        Returns:
            хеш изображения или None
        """
        try:
            # Используем perceptual hash (pHash) для сравнения по содержимому
            return imagehash.phash(image)
        except Exception as e:
            print(f"Ошибка вычисления хеша изображения: {e}")
            return None
    
    def calculate_similarity(self, hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> float:
        """
        Вычислить схожесть двух изображений по их хешам
        
        Args:
            hash1: хеш первого изображения
            hash2: хеш второго изображения
            
        Returns:
            коэффициент схожести (0-1), где 1 = идентичные
        """
        if hash1 is None or hash2 is None:
            return 0.0
        
        # Вычисляем расстояние между хешами
        distance = hash1 - hash2
        
        # Максимальное расстояние для pHash обычно 64
        max_distance = 64.0
        
        # Преобразуем расстояние в коэффициент схожести
        similarity = 1.0 - (distance / max_distance)
        
        return max(0.0, min(1.0, similarity))
    
    def compare_images(self, image1: Image.Image, image2: Image.Image) -> float:
        """
        Сравнить два изображения
        
        Args:
            image1: первое изображение
            image2: второе изображение
            
        Returns:
            коэффициент схожести (0-1)
        """
        hash1 = self.calculate_image_hash(image1)
        hash2 = self.calculate_image_hash(image2)
        
        if hash1 is None or hash2 is None:
            return 0.0
        
        return self.calculate_similarity(hash1, hash2)
    
    def find_similar_images(self, image_path: Path, other_images: List[Path]) -> List[Tuple[Path, float]]:
        """
        Найти похожие изображения для данного
        
        Args:
            image_path: путь к изображению
            other_images: список других изображений для сравнения
            
        Returns:
            список кортежей (путь к изображению, коэффициент схожести)
        """
        image = self.load_image(image_path)
        if image is None:
            return []
        
        image_hash = self.calculate_image_hash(image)
        if image_hash is None:
            return []
        
        results = []
        
        for other_path in other_images:
            if other_path == image_path:
                continue
            
            if not self.config.is_supported_image(other_path):
                continue
            
            other_image = self.load_image(other_path)
            if other_image is None:
                continue
            
            other_hash = self.calculate_image_hash(other_image)
            if other_hash is None:
                continue
            
            similarity = self.calculate_similarity(image_hash, other_hash)
            
            if similarity >= self.threshold:
                results.append((other_path, similarity))
        
        return results
    
    def find_all_duplicates(self, image_files: List[Path]) -> List[Tuple[Path, Path, float]]:
        """
        Найти все пары дублирующихся изображений
        
        Args:
            image_files: список путей к изображениям
            
        Returns:
            список кортежей (путь1, путь2, коэффициент схожести)
        """
        results = []
        processed = set()
        
        for i, image1_path in enumerate(image_files):
            if not self.config.is_supported_image(image1_path):
                continue
            
            image1 = self.load_image(image1_path)
            if image1 is None:
                continue
            
            hash1 = self.calculate_image_hash(image1)
            if hash1 is None:
                continue
            
            for image2_path in image_files[i+1:]:
                if not self.config.is_supported_image(image2_path):
                    continue
                
                # Пропускаем уже обработанные пары
                pair_key = tuple(sorted([str(image1_path), str(image2_path)]))
                if pair_key in processed:
                    continue
                processed.add(pair_key)
                
                image2 = self.load_image(image2_path)
                if image2 is None:
                    continue
                
                hash2 = self.calculate_image_hash(image2)
                if hash2 is None:
                    continue
                
                similarity = self.calculate_similarity(hash1, hash2)
                
                if similarity >= self.threshold:
                    results.append((image1_path, image2_path, similarity))
        
        return results

