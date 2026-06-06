"""Модуль для создания базы данных и таблиц PostgreSQL."""

from typing import Any

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection

from config import DB_CONFIG


class DatabaseManager:
    """Класс для создания базы данных и таблиц PostgreSQL."""

    def __init__(self, db_config: dict[str, Any] | None = None) -> None:
        """
        Инициализирует менеджер базы данных.

        :param db_config: Параметры подключения к PostgreSQL.
        """
        self.db_config = db_config or DB_CONFIG

    def _get_connection(self, database: str | None = None) -> PgConnection:
        """
        Создает подключение к PostgreSQL.

        :param database: Имя базы данных. Если None, используется из конфигурации.
        :return: Активное подключение к PostgreSQL.
        """
        return psycopg2.connect(
            host=self.db_config["host"],
            port=self.db_config["port"],
            user=self.db_config["user"],
            password=self.db_config["password"],
            dbname=database or self.db_config["dbname"],
        )

    def create_database(self) -> None:
        """
        Создает базу данных, если она еще не существует.

        Подключается к служебной БД postgres и выполняет CREATE DATABASE.
        """
        db_name = self.db_config["dbname"]

        with self._get_connection("postgres") as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (db_name,),
                )
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute(
                        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
                    )
                    print(f"База данных '{db_name}' успешно создана.")
                else:
                    print(f"База данных '{db_name}' уже существует.")

    def create_tables(self) -> None:
        """Создает таблицы companies и vacancies с внешним ключом."""
        create_companies_table = """
            CREATE TABLE IF NOT EXISTS companies (
                company_id VARCHAR(32) PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                company_url TEXT
            );
        """

        create_vacancies_table = """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id VARCHAR(32) PRIMARY KEY,
                company_id VARCHAR(32) NOT NULL REFERENCES companies(company_id),
                vacancy_name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                salary_avg INTEGER,
                currency VARCHAR(10),
                vacancy_url TEXT,
                area VARCHAR(255),
                published_at TIMESTAMP
            );
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_companies_table)
                cursor.execute(create_vacancies_table)
            conn.commit()
            print("Таблицы companies и vacancies успешно созданы.")

    def clear_tables(self) -> None:
        """Очищает таблицы vacancies и companies перед повторной загрузкой данных."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE vacancies RESTART IDENTITY CASCADE;")
                cursor.execute("TRUNCATE TABLE companies RESTART IDENTITY CASCADE;")
            conn.commit()

    def insert_companies(self, companies: list[dict[str, Any]]) -> None:
        """
        Заполняет таблицу companies данными о работодателях.

        :param companies: Список компаний для вставки.
        """
        insert_query = """
            INSERT INTO companies (company_id, company_name, company_url)
            VALUES (%(company_id)s, %(company_name)s, %(company_url)s)
            ON CONFLICT (company_id) DO UPDATE
            SET company_name = EXCLUDED.company_name,
                company_url = EXCLUDED.company_url;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(insert_query, companies)
            conn.commit()

        print(f"В таблицу companies добавлено записей: {len(companies)}.")

    def insert_vacancies(self, vacancies: list[dict[str, Any]]) -> None:
        """
        Заполняет таблицу vacancies данными о вакансиях.

        :param vacancies: Список вакансий для вставки.
        """
        insert_query = """
            INSERT INTO vacancies (
                vacancy_id,
                company_id,
                vacancy_name,
                salary_from,
                salary_to,
                salary_avg,
                currency,
                vacancy_url,
                area,
                published_at
            )
            VALUES (
                %(vacancy_id)s,
                %(company_id)s,
                %(vacancy_name)s,
                %(salary_from)s,
                %(salary_to)s,
                %(salary_avg)s,
                %(currency)s,
                %(vacancy_url)s,
                %(area)s,
                %(published_at)s
            )
            ON CONFLICT (vacancy_id) DO UPDATE
            SET company_id = EXCLUDED.company_id,
                vacancy_name = EXCLUDED.vacancy_name,
                salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                salary_avg = EXCLUDED.salary_avg,
                currency = EXCLUDED.currency,
                vacancy_url = EXCLUDED.vacancy_url,
                area = EXCLUDED.area,
                published_at = EXCLUDED.published_at;
        """

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(insert_query, vacancies)
            conn.commit()

        print(f"В таблицу vacancies добавлено записей: {len(vacancies)}.")

    def fill_database(self, companies: list[dict[str, Any]], vacancies: list[dict[str, Any]]) -> None:
        """
        Очищает таблицы и загружает актуальные данные.

        :param companies: Список компаний.
        :param vacancies: Список вакансий.
        """
        self.clear_tables()
        self.insert_companies(companies)
        self.insert_vacancies(vacancies)
