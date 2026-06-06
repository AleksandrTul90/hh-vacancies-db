"""Модуль для взаимодействия с публичным API hh.ru."""

from typing import Any

import requests

from config import HH_API_BASE_URL, HH_USER_AGENT


class HeadHunterAPI:
    """Клиент для получения данных о работодателях и вакансиях с hh.ru."""

    def __init__(self, base_url: str = HH_API_BASE_URL, timeout: int = 10) -> None:
        """
        Инициализирует клиент API.

        :param base_url: Базовый URL API hh.ru.
        :param timeout: Таймаут HTTP-запросов в секундах.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"User-Agent": HH_USER_AGENT}

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Выполняет GET-запрос к API.

        :param endpoint: Путь эндпоинта без базового URL.
        :param params: Параметры запроса.
        :return: Ответ API в формате словаря.
        :raises requests.HTTPError: При ошибке HTTP.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def is_available(self) -> bool:
        """
        Проверяет доступность API hh.ru.

        :return: True, если API отвечает, иначе False.
        """
        try:
            self._get("employers/1740")
            return True
        except (requests.RequestException, ValueError):
            return False

    def get_employer(self, employer_id: str) -> dict[str, Any]:
        """
        Получает информацию о работодателе.

        :param employer_id: Идентификатор работодателя на hh.ru.
        :return: Данные работодателя.
        """
        return self._get(f"employers/{employer_id}")

    def get_vacancies_by_employer(
        self,
        employer_id: str,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Получает список вакансий работодателя.

        :param employer_id: Идентификатор работодателя.
        :param per_page: Количество вакансий на странице.
        :return: Список вакансий работодателя.
        """
        vacancies: list[dict[str, Any]] = []
        page = 0

        while True:
            data = self._get(
                "vacancies",
                params={
                    "employer_id": employer_id,
                    "per_page": per_page,
                    "page": page,
                },
            )
            items = data.get("items", [])
            vacancies.extend(items)

            pages = data.get("pages", 1)
            if page >= pages - 1:
                break
            page += 1

        return vacancies
