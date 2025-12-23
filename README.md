# Duplicate Manager

Система управления дублирующимися файлами в системе.

## Возможности

### Уровень 1: Поиск одинаковых файлов по содержанию
- Поиск точных дубликатов по хешам (MD5/SHA256)
- Быстрая индексация файлов
- Поддержка всех типов файлов

### Уровень 2: Поиск вложенных текстовых файлов
- Определение, когда один текстовый файл содержит содержимое другого
- Работа с различными кодировками
- Настраиваемый порог совпадения

### Уровень 3: Сравнение изображений
- Сравнение изображений по содержимому (независимо от формата)
- Поддержка различных форматов (JPEG, PNG, BMP, GIF, WebP и др.)
- Определение похожих изображений с настраиваемым порогом

## Особенности

- ✅ Работает локально (без интернета)
- ✅ Параметризация поиска и индексации
- ✅ Поддержка съемных носителей и облачных хранилищ
- ✅ Оптимизированное быстродействие
- ✅ Портативность (работа на флешке, несколько устройств)
- ✅ Интерактивные действия с найденными дубликатами

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/GRUUUUDD/dublicate.git
cd dublicate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

Или используйте виртуальное окружение (рекомендуется):

```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Первый запуск

```bash
# Сканирование директории
python3 -m duplicate_manager scan /path/to/directory

# Поиск дубликатов
python3 -m duplicate_manager find --level 1
```

## Использование

### Основные команды

```bash
# Сканирование директории и создание индекса
python3 -m duplicate_manager scan <путь>
python3 -m duplicate_manager scan . --no-progress  # Без прогресс-бара

# Поиск дубликатов разных уровней
python3 -m duplicate_manager find --level 1  # Точные дубликаты
python3 -m duplicate_manager find --level 2  # Вложенные тексты
python3 -m duplicate_manager find --level 3  # Похожие изображения

# Сохранение результатов в файл
python3 -m duplicate_manager find --level 1 --output results.txt

# Интерактивный режим для работы с дубликатами
python3 -m duplicate_manager interactive

# Статистика по индексу
python3 -m duplicate_manager stats

# Очистка индекса
python3 -m duplicate_manager clear-index
```

### Примеры использования

```bash
# Сканировать домашнюю директорию
python3 -m duplicate_manager scan ~

# Найти все точные дубликаты
python3 -m duplicate_manager find --level 1

# Найти похожие изображения
python3 -m duplicate_manager find --level 3

# Интерактивная работа с найденными дубликатами
python3 -m duplicate_manager interactive
```

## Конфигурация

При первом запуске автоматически создается файл `config.json` с настройками по умолчанию. Вы можете изменить параметры:

```json
{
  "hash_algorithm": "md5",
  "min_file_size": 0,
  "max_file_size": null,
  "exclude_patterns": [".git", "__pycache__", "node_modules"],
  "exclude_extensions": [".tmp", ".swp", ".DS_Store"],
  "image_similarity_threshold": 0.95,
  "text_containment_threshold": 0.8,
  "index_path": ".duplicate_index",
  "chunk_size": 8192,
  "supported_image_formats": [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"],
  "supported_text_extensions": [".txt", ".py", ".js", ".html", ".css", ".md", ".json", ".xml", ".csv"]
}
```

## Требования

- Python 3.7+
- Зависимости указаны в `requirements.txt`

## Структура проекта

```
duplicate_manager/
├── duplicate_manager/      # Основной пакет
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py           # Конфигурация
│   ├── hasher.py           # УР1: Хеширование
│   ├── text_matcher.py     # УР2: Текстовые файлы
│   ├── image_matcher.py    # УР3: Изображения
│   ├── indexer.py          # Индексация
│   ├── scanner.py           # Сканирование
│   ├── actions.py           # Действия с файлами
│   └── cli.py              # CLI интерфейс
├── requirements.txt        # Зависимости
├── setup.py               # Установка пакета
└── README.md              # Документация
```

## Лицензия

MIT License

## Автор

GRUUUUDD
