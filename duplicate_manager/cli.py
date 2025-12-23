"""
CLI интерфейс для duplicate_manager
"""

import click
from pathlib import Path
from typing import List
from duplicate_manager.config import Config
from duplicate_manager.scanner import FileScanner
from duplicate_manager.actions import FileActions


@click.group()
@click.option('--config', type=click.Path(exists=True), help='Путь к файлу конфигурации')
@click.pass_context
def cli(ctx, config):
    """Duplicate Manager - система управления дублирующимися файлами"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config_path=config)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--no-progress', is_flag=True, help='Не показывать прогресс-бар')
@click.pass_context
def scan(ctx, path, no_progress):
    """Сканировать директорию и создать индекс"""
    config = ctx.obj['config']
    scanner = FileScanner(config)
    
    directory = Path(path)
    click.echo(f"Сканирование директории: {directory}")
    
    scanner.scan_directory(directory, show_progress=not no_progress)
    
    stats = scanner.get_statistics()
    click.echo(f"\nСтатистика:")
    click.echo(f"  Всего файлов: {stats['total_files']}")
    click.echo(f"  Уникальных: {stats['unique_files']}")
    click.echo(f"  Групп дубликатов: {stats['duplicate_groups']}")
    click.echo(f"  Общий размер: {stats['total_size_mb']:.2f} MB")
    if stats['wasted_space_bytes'] > 0:
        click.echo(f"  Потенциальная экономия: {stats['wasted_space_bytes'] / (1024*1024):.2f} MB")


@cli.command()
@click.option('--level', type=click.IntRange(1, 3), default=1, help='Уровень поиска (1-3)')
@click.option('--output', type=click.Path(), help='Сохранить результаты в файл')
@click.pass_context
def find(ctx, level, output):
    """Найти дубликаты"""
    config = ctx.obj['config']
    scanner = FileScanner(config)
    
    results = []
    
    if level == 1:
        click.echo("Поиск точных дубликатов (УР1)...")
        duplicates = scanner.find_exact_duplicates()
        
        if duplicates:
            click.echo(f"\nНайдено групп дубликатов: {len(duplicates)}")
            for file_hash, file_paths in duplicates.items():
                click.echo(f"\nХеш: {file_hash[:16]}...")
                for file_path in file_paths:
                    click.echo(f"  - {file_path}")
                results.append(('exact', file_hash, file_paths))
        else:
            click.echo("Дубликаты не найдены")
    
    elif level == 2:
        click.echo("Поиск вложенных текстовых файлов (УР2)...")
        containments = scanner.find_text_containments()
        
        if containments:
            click.echo(f"\nНайдено пар: {len(containments)}")
            for container, contained, similarity in containments:
                click.echo(f"\nСхожесть: {similarity:.2%}")
                click.echo(f"  Контейнер: {container}")
                click.echo(f"  Содержимое: {contained}")
                results.append(('text_containment', container, contained, similarity))
        else:
            click.echo("Вложенные файлы не найдены")
    
    elif level == 3:
        click.echo("Поиск дублирующихся изображений (УР3)...")
        image_duplicates = scanner.find_image_duplicates()
        
        if image_duplicates:
            click.echo(f"\nНайдено пар: {len(image_duplicates)}")
            for img1, img2, similarity in image_duplicates:
                click.echo(f"\nСхожесть: {similarity:.2%}")
                click.echo(f"  {img1}")
                click.echo(f"  {img2}")
                results.append(('image_duplicate', img1, img2, similarity))
        else:
            click.echo("Дублирующиеся изображения не найдены")
    
    # Сохранение результатов в файл
    if output and results:
        output_path = Path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(str(result) + '\n')
        click.echo(f"\nРезультаты сохранены в: {output_path}")


@cli.command()
@click.pass_context
def interactive(ctx):
    """Интерактивный режим для работы с дубликатами"""
    config = ctx.obj['config']
    scanner = FileScanner(config)
    actions = FileActions(scanner.index)
    
    click.echo("=== Интерактивный режим ===")
    
    # Показываем все уровни
    click.echo("\n1. Точные дубликаты (УР1)")
    duplicates = scanner.find_exact_duplicates()
    
    if not duplicates:
        click.echo("Дубликаты не найдены. Сначала выполните сканирование.")
        return
    
    click.echo(f"Найдено групп: {len(duplicates)}")
    
    # Показываем первые 10 групп
    groups_list = list(duplicates.items())[:10]
    
    for idx, (file_hash, file_paths) in enumerate(groups_list, 1):
        click.echo(f"\n--- Группа {idx} ---")
        click.echo(f"Файлов: {len(file_paths)}")
        for i, file_path in enumerate(file_paths, 1):
            size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
            click.echo(f"  {i}. {file_path} ({size / 1024:.1f} KB)")
        
        if click.confirm(f"\nВыполнить действие с группой {idx}?"):
            click.echo("\nДоступные действия:")
            click.echo("  1. Удалить все кроме первого")
            click.echo("  2. Переместить дубликаты в папку")
            click.echo("  3. Пропустить")
            
            choice = click.prompt("Выберите действие", type=int, default=3)
            
            if choice == 1:
                if click.confirm("Удалить все дубликаты кроме первого?"):
                    deleted = actions.delete_duplicates_keep_one(file_paths, keep_index=0)
                    click.echo(f"Удалено файлов: {deleted}")
            
            elif choice == 2:
                target_folder = click.prompt("Введите путь к папке", type=str)
                target_path = Path(target_folder)
                if target_path.exists() or click.confirm(f"Создать папку {target_path}?"):
                    target_path.mkdir(parents=True, exist_ok=True)
                    moved = actions.move_duplicates_to_folder(file_paths, target_path, keep_index=0)
                    click.echo(f"Перемещено файлов: {moved}")
    
    if len(duplicates) > 10:
        click.echo(f"\n... и еще {len(duplicates) - 10} групп")


@cli.command()
@click.pass_context
def stats(ctx):
    """Показать статистику по индексу"""
    config = ctx.obj['config']
    scanner = FileScanner(config)
    
    stats = scanner.get_statistics()
    
    click.echo("=== Статистика ===")
    click.echo(f"Всего файлов: {stats['total_files']}")
    click.echo(f"Уникальных файлов: {stats['unique_files']}")
    click.echo(f"Групп дубликатов: {stats['duplicate_groups']}")
    click.echo(f"Общий размер: {stats['total_size_mb']:.2f} MB")
    
    if stats['wasted_space_bytes'] > 0:
        wasted_mb = stats['wasted_space_bytes'] / (1024 * 1024)
        click.echo(f"Потенциальная экономия места: {wasted_mb:.2f} MB")


@cli.command()
@click.confirmation_option(prompt='Вы уверены? Это удалит весь индекс.')
@click.pass_context
def clear_index(ctx):
    """Очистить индекс"""
    config = ctx.obj['config']
    scanner = FileScanner(config)
    
    scanner.index.clear()
    scanner.index.save()
    click.echo("Индекс очищен")


if __name__ == '__main__':
    cli()

