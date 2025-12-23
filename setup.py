"""
Setup script для duplicate_manager
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="duplicate-manager",
    version="1.0.0",
    description="Система управления дублирующимися файлами в системе",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="",
    packages=find_packages(),
    install_requires=[
        "Pillow>=10.0.0",
        "imagehash>=4.3.1",
        "tqdm>=4.66.0",
        "click>=8.1.0",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "duplicate-manager=duplicate_manager.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

