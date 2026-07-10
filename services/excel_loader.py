"""Загрузка и валидация Excel-файлов через pandas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class ExcelLoader:
    """Читает Excel-листы и помогает безопасно брать значения по заголовкам."""

    def load_sheet(self, file_path: str | Path, sheet_name: str) -> pd.DataFrame:
        """Загружает лист Excel в DataFrame как строки.

        Пустые значения сохраняются как пустые строки, чтобы потом их было проще
        обрабатывать без NaN в интерфейсе и логике замен.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {path}")

        try:
            dataframe = pd.read_excel(
                path,
                sheet_name=sheet_name,
                dtype=str,
                engine="openpyxl",
                keep_default_na=False,
            )
        except ValueError as error:
            raise ValueError(f"Лист '{sheet_name}' не найден в файле {path.name}") from error
        except Exception as error:
            raise RuntimeError(f"Не удалось прочитать файл {path.name}: {error}") from error

        dataframe.columns = [str(column).strip() for column in dataframe.columns]
        return dataframe.fillna("")

    def validate_columns(
        self,
        dataframe: pd.DataFrame,
        required_columns: list[str],
        context: str,
    ) -> None:
        """Проверяет наличие обязательных столбцов."""
        missing = [column for column in required_columns if column not in dataframe.columns]
        if missing:
            missing_str = ", ".join(missing)
            raise KeyError(f"В '{context}' отсутствуют столбцы: {missing_str}")

    def get_first_non_empty_value(
        self,
        dataframe: pd.DataFrame,
        column_name: str,
        context: str,
    ) -> str:
        """Возвращает первое непустое значение из столбца."""
        self.validate_columns(dataframe, [column_name], context)
        series = dataframe[column_name].astype(str).str.strip()
        values = [value for value in series.tolist() if value]
        if not values:
            raise ValueError(f"В '{context}' столбец '{column_name}' не содержит данных")
        return values[0]

    def get_first_non_empty_row(
        self,
        dataframe: pd.DataFrame,
        required_columns: list[str],
        context: str,
    ) -> dict[str, str]:
        """Возвращает первую строку, где хотя бы одно обязательное поле заполнено."""
        self.validate_columns(dataframe, required_columns, context)

        for _, row in dataframe.iterrows():
            row_data = {
                column: str(row.get(column, "")).strip()
                for column in dataframe.columns
            }
            if any(row_data.get(column, "") for column in required_columns):
                return row_data

        raise ValueError(f"В '{context}' не найдено ни одной заполненной строки")
