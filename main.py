"""Точка входа в проект поиска вакансий с подключением к PostgreSQL."""

import psycopg2

from database import DatabaseManager
from db_manager import DBManager
from vacancies import VacancyService


def interact_with_user(db_manager: DBManager) -> None:
    """
    Запускает консольное меню для взаимодействия с данными в базе.

    :param db_manager: Экземпляр класса DBManager.
    """
    menu = {
        "1": "Показать компании и количество вакансий",
        "2": "Показать все вакансии",
        "3": "Показать среднюю зарплату",
        "4": "Показать вакансии с зарплатой выше средней",
        "5": "Найти вакансии по ключевому слову",
        "0": "Выход",
    }

    while True:
        print("\n=== Меню работы с вакансиями ===")
        for key, description in menu.items():
            print(f"{key}. {description}")

        choice = input("\nВыберите пункт меню: ").strip()

        if choice == "0":
            print("Работа программы завершена.")
            break

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            if not companies:
                print("Компании не найдены.")
                continue

            print("\nСписок компаний и количество вакансий:")
            for company_name, vacancies_count in companies:
                print(f"- {company_name}: {vacancies_count} вакансий")
            continue

        if choice == "2":
            vacancies = db_manager.get_all_vacancies()
            if not vacancies:
                print("Вакансии не найдены.")
                continue

            print("\nСписок всех вакансий:")
            for company_name, vacancy_name, salary, vacancy_url in vacancies:
                print(
                    f"- {company_name} | {vacancy_name} | {salary} | {vacancy_url}"
                )
            continue

        if choice == "3":
            avg_salary = db_manager.get_avg_salary()
            if avg_salary is None:
                print("Недостаточно данных для расчета средней зарплаты.")
                continue

            print(f"\nСредняя зарплата по вакансиям: {avg_salary:,.0f} руб.")
            continue

        if choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            if not vacancies:
                print("Вакансии с зарплатой выше средней не найдены.")
                continue

            print("\nВакансии с зарплатой выше средней:")
            for company_name, vacancy_name, salary_avg, vacancy_url in vacancies:
                print(
                    f"- {company_name} | {vacancy_name} | "
                    f"{salary_avg:,.0f} руб. | {vacancy_url}"
                )
            continue

        if choice == "5":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым.")
                continue

            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            if not vacancies:
                print(f"Вакансии по запросу '{keyword}' не найдены.")
                continue

            print(f"\nВакансии, содержащие слово '{keyword}':")
            for company_name, vacancy_name, salary, vacancy_url in vacancies:
                print(
                    f"- {company_name} | {vacancy_name} | {salary} | {vacancy_url}"
                )
            continue

        print("Некорректный пункт меню. Попробуйте еще раз.")


def main() -> None:
    """Инициализирует БД, загружает данные и запускает пользовательский интерфейс."""
    database_manager = DatabaseManager()
    vacancy_service = VacancyService()

    try:
        print("=== Инициализация базы данных ===")
        database_manager.create_database()
        database_manager.create_tables()

        print("\n=== Загрузка данных о компаниях и вакансиях ===")
        companies, vacancies = vacancy_service.collect_data()
        database_manager.fill_database(companies, vacancies)

        print("\n=== База данных готова к работе ===")
        db_manager = DBManager()
        interact_with_user(db_manager)
    except psycopg2.OperationalError:
        print(
            "Не удалось подключиться к PostgreSQL. "
            "Проверьте, что сервер запущен, и настройки в файле .env."
        )


if __name__ == "__main__":
    main()
