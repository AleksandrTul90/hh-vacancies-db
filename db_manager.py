"""Модуль с классом DBManager для работы с данными в PostgreSQL."""

from typing import Any

import psycopg2
from psycopg2.extensions import connection as PgConnection

from config import DB_CONFIG


class DBManager:
    """Класс для получения аналитических данных о компаниях и вакансиях из БД."""

    def __init__(self, db_config: dict[str, Any] | None = None) -> None:
        """
        Инициализирует менеджер для работы с базой данных.

        :param db_config: Параметры подключения к PostgreSQL.
        """
        self.db_config = db_config or DB_CONFIG

    def _get_connection(self) -> PgConnection:
        """
        Создает подключение к базе данных проекта.

        :return: Активное подключение к PostgreSQL.
        """
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            dbname=self.db_config["dbname"],
        )

    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        :return: Список кортежей (название компании, количество вакансий).
        """
        query = """
            SELECT
                c.company_name,
                COUNT(v.vacancy_id) AS vacancies_count
            FROM companies c
            LEFT JOIN vacancies v ON c.company_id = v.company_id
            GROUP BY c.company_id, c.company_name
            ORDER BY vacancies_count DESC, c.company_name;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_all_vacancies(self) -> list[tuple[str, str, str, str]]:
        """
        Получает список всех вакансий с данными о компании и зарплате.

        :return: Список кортежей (компания, вакансия, зарплата, ссылка).
        """
        query = """
            SELECT
                c.company_name,
                v.vacancy_name,
                CASE
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                        THEN v.salary_from::TEXT || ' - ' || v.salary_to::TEXT || ' ' || COALESCE(v.currency, '')
                    WHEN v.salary_from IS NOT NULL
                        THEN 'от ' || v.salary_from::TEXT || ' ' || COALESCE(v.currency, '')
                    WHEN v.salary_to IS NOT NULL
                        THEN 'до ' || v.salary_to::TEXT || ' ' || COALESCE(v.currency, '')
                    ELSE 'Зарплата не указана'
                END AS salary,
                v.vacancy_url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            ORDER BY c.company_name, v.vacancy_name;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_avg_salary(self) -> float | None:
        """
        Получает среднюю зарплату по вакансиям.

        :return: Средняя зарплата или None, если данных нет.
        """
        query = """
            SELECT AVG(salary_avg)
            FROM vacancies
            WHERE salary_avg IS NOT NULL;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()

        if result and result[0] is not None:
            return float(result[0])
        return None

    def get_vacancies_with_higher_salary(self) -> list[tuple[str, str, int, str]]:
        """
        Получает вакансии, у которых зарплата выше средней по всем вакансиям.

        :return: Список кортежей (компания, вакансия, зарплата, ссылка).
        """
        query = """
            SELECT
                c.company_name,
                v.vacancy_name,
                v.salary_avg,
                v.vacancy_url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            WHERE v.salary_avg > (
                SELECT AVG(salary_avg)
                FROM vacancies
                WHERE salary_avg IS NOT NULL
            )
            ORDER BY v.salary_avg DESC;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple[str, str, str, str]]:
        """
        Получает вакансии, в названии которых содержится ключевое слово.

        :param keyword: Ключевое слово для поиска, например python.
        :return: Список кортежей (компания, вакансия, зарплата, ссылка).
        """
        query = """
            SELECT
                c.company_name,
                v.vacancy_name,
                CASE
                    WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL
                        THEN v.salary_from::TEXT || ' - ' || v.salary_to::TEXT || ' ' || COALESCE(v.currency, '')
                    WHEN v.salary_from IS NOT NULL
                        THEN 'от ' || v.salary_from::TEXT || ' ' || COALESCE(v.currency, '')
                    WHEN v.salary_to IS NOT NULL
                        THEN 'до ' || v.salary_to::TEXT || ' ' || COALESCE(v.currency, '')
                    ELSE 'Зарплата не указана'
                END AS salary,
                v.vacancy_url
            FROM vacancies v
            JOIN companies c ON v.company_id = c.company_id
            WHERE LOWER(v.vacancy_name) LIKE LOWER(%s)
            ORDER BY c.company_name, v.vacancy_name;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (f"%{keyword}%",))
                return cursor.fetchall()
