"""Работа с папкой шаблонов и копированием исходного файла."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from config.settings import TEMP_DIR, TEMPLATES_DIR, ensure_runtime_directories


class TemplateManager:
    """Умеет находить шаблоны, делать их рабочую копию и сохранять результат."""

    def __init__(self) -> None:
        ensure_runtime_directories()

    def get_template_directory(self, branch: str, bbu_type: str) -> Path:
        """Возвращает каталог шаблонов для выбранного филиала и типа BBU."""
        return TEMPLATES_DIR / branch / bbu_type

    def list_templates(self, branch: str, bbu_type: str) -> list[str]:
        """Собирает список Excel-шаблонов из нужной папки."""
        directory = self.get_template_directory(branch, bbu_type)
        if not directory.exists():
            return []

        templates = [
            path.name
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in {".xlsx", ".xlsm"}
        ]
        return sorted(templates, key=str.lower)

    def get_template_path(self, branch: str, bbu_type: str, template_name: str) -> Path:
        """Формирует абсолютный путь к выбранному шаблону."""
        template_path = self.get_template_directory(branch, bbu_type) / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")
        return template_path

    def create_working_copy(self, template_path: str | Path, ne_name: str | None = None) -> Path:
        """Создает рабочую копию шаблона во временной папке проекта."""
        source = Path(template_path)
        if not source.exists():
            raise FileNotFoundError(f"Файл шаблона не найден: {source}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_ne_name = (ne_name or source.stem).replace("/", "_").replace("\\", "_").strip()
        filename = f"{safe_ne_name}_{timestamp}{source.suffix}"
        target = TEMP_DIR / filename
        shutil.copy2(source, target)
        return target

    def save_result(self, working_file: str | Path, target_path: str | Path) -> Path:
        """Сохраняет итоговый файл в выбранное пользователем место."""
        source = Path(working_file)
        destination = Path(target_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return destination

    def open_templates_folder(self) -> None:
        """Открывает папку шаблонов системным способом."""
        ensure_runtime_directories()

        if sys.platform.startswith("win"):
            import os

            os.startfile(TEMPLATES_DIR)  # type: ignore[attr-defined]
            return

        if sys.platform == "darwin":
            subprocess.run(["open", str(TEMPLATES_DIR)], check=False)
            return

        subprocess.run(["xdg-open", str(TEMPLATES_DIR)], check=False)
