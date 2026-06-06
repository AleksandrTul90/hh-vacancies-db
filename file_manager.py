"""Модуль для взаимодействия с файлами."""

import json
from pathlib import Path
from typing import Any


class FileManager:
    """Класс для чтения и записи данных из файлов."""

    def __init__(self, file_path: Path) -> None:
        """
        Инициализирует менеджер файлов.

        :param file_path: Путь к файлу с данными.
        """
        self.file_path = file_path

    def read_json(self) -> dict[str, Any]:
        """
        Читает JSON-файл и возвращает его содержимое.

        :return: Данные из JSON-файла.
        :raises FileNotFoundError: Если файл не найден.
        :raises json.JSONDecodeError: Если файл содержит некорректный JSON.
        """
        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def get_vacancies_from_file(self) -> list[dict[str, Any]]:
        """
        Возвращает список вакансий из подготовленного файла.

        :return: Список вакансий в формате API hh.ru.
        """
        data = self.read_json()
        return data.get("items", [])
