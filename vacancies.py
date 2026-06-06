"""Модуль для обработки вакансий и подготовки данных к загрузке в БД."""

from typing import Any

from api_hh import HeadHunterAPI
from config import FALLBACK_COMPANIES, SAMPLE_VACANCIES_FILE, TARGET_EMPLOYER_IDS
from file_manager import FileManager


class VacancyService:
    """Сервис сбора и преобразования данных о компаниях и вакансиях."""

    def __init__(self, api_client: HeadHunterAPI | None = None) -> None:
        """
        Инициализирует сервис вакансий.

        :param api_client: Клиент API hh.ru. Если не передан, создается новый.
        """
        self.api_client = api_client or HeadHunterAPI()
        self.file_manager = FileManager(SAMPLE_VACANCIES_FILE)

    @staticmethod
    def _calculate_average_salary(
        salary_from: int | None,
        salary_to: int | None,
    ) -> int | None:
        """
        Рассчитывает среднее значение зарплаты по вилке.

        :param salary_from: Нижняя граница зарплаты.
        :param salary_to: Верхняя граница зарплаты.
        :return: Средняя зарплата или None, если данных нет.
        """
        if salary_from is not None and salary_to is not None:
            return int((salary_from + salary_to) / 2)
        if salary_from is not None:
            return salary_from
        if salary_to is not None:
            return salary_to
        return None

    def _parse_vacancy(self, vacancy: dict[str, Any]) -> dict[str, Any]:
        """
        Преобразует вакансию из API в формат для таблицы vacancies.

        :param vacancy: Вакансия в формате API hh.ru.
        :return: Словарь с полями для вставки в БД.
        """
        salary = vacancy.get("salary") or {}
        salary_from = salary.get("from")
        salary_to = salary.get("to")
        employer = vacancy.get("employer") or {}
        area = vacancy.get("area") or {}

        return {
            "vacancy_id": vacancy["id"],
            "company_id": employer.get("id"),
            "vacancy_name": vacancy.get("name", ""),
            "salary_from": salary_from,
            "salary_to": salary_to,
            "salary_avg": self._calculate_average_salary(salary_from, salary_to),
            "currency": salary.get("currency"),
            "vacancy_url": vacancy.get("alternate_url", ""),
            "area": area.get("name"),
            "published_at": vacancy.get("published_at"),
        }

    def _parse_employer(self, employer: dict[str, Any]) -> dict[str, Any]:
        """
        Преобразует работодателя из API в формат для таблицы companies.

        :param employer: Работодатель в формате API hh.ru.
        :return: Словарь с полями для вставки в БД.
        """
        return {
            "company_id": employer["id"],
            "company_name": employer.get("name", ""),
            "company_url": employer.get("alternate_url", ""),
        }

    def collect_companies_from_api(self) -> list[dict[str, Any]]:
        """
        Получает данные о компаниях через API hh.ru.

        :return: Список компаний для таблицы companies.
        """
        companies: list[dict[str, Any]] = []

        for employer_id in TARGET_EMPLOYER_IDS:
            employer_data = self.api_client.get_employer(employer_id)
            companies.append(self._parse_employer(employer_data))

        return companies

    def collect_vacancies_from_api(self) -> list[dict[str, Any]]:
        """
        Получает вакансии выбранных компаний через API hh.ru.

        :return: Список вакансий для таблицы vacancies.
        """
        vacancies: list[dict[str, Any]] = []

        for employer_id in TARGET_EMPLOYER_IDS:
            employer_vacancies = self.api_client.get_vacancies_by_employer(employer_id)
            for vacancy in employer_vacancies:
                vacancies.append(self._parse_vacancy(vacancy))

        return vacancies

    def collect_companies_from_file(self) -> list[dict[str, Any]]:
        """
        Формирует список компаний на основе подготовленного JSON-файла.

        :return: Список компаний для таблицы companies.
        """
        vacancies = self.file_manager.get_vacancies_from_file()
        companies_map: dict[str, dict[str, Any]] = {}

        for vacancy in vacancies:
            employer = vacancy.get("employer") or {}
            company_id = employer.get("id")
            if company_id and company_id not in companies_map:
                companies_map[company_id] = self._parse_employer(employer)

        companies = list(companies_map.values())

        existing_ids = {company["company_id"] for company in companies}
        for company in FALLBACK_COMPANIES:
            if company["company_id"] not in existing_ids:
                companies.append(company)

        return companies[:10]

    def collect_vacancies_from_file(self) -> list[dict[str, Any]]:
        """
        Получает вакансии из подготовленного JSON-файла.

        :return: Список вакансий для таблицы vacancies.
        """
        raw_vacancies = self.file_manager.get_vacancies_from_file()
        return [self._parse_vacancy(vacancy) for vacancy in raw_vacancies]

    def collect_data(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Собирает данные о компаниях и вакансиях из API или файла-заглушки.

        :return: Кортеж (список компаний, список вакансий).
        """
        if self.api_client.is_available():
            print("API hh.ru доступен. Загружаем данные через API...")
            companies = self.collect_companies_from_api()
            vacancies = self.collect_vacancies_from_api()
            return companies, vacancies

        print("API hh.ru недоступен. Используем подготовленные данные из файла...")
        companies = self.collect_companies_from_file()
        vacancies = self.collect_vacancies_from_file()
        return companies, vacancies
