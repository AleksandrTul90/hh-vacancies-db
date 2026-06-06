"""Конфигурация проекта и список отслеживаемых компаний."""

from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_VACANCIES_FILE = DATA_DIR / "hh_vacancies_sample.json"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "dbname": os.getenv("DB_NAME", "hh_vacancies"),
}

HH_API_BASE_URL = "https://api.hh.ru"
HH_USER_AGENT = "HH-Vacancies-Project/1.0 (student-project@example.com)"

# Не менее 10 компаний для сбора вакансий (ID работодателей на hh.ru).
TARGET_EMPLOYER_IDS = [
    "1740",    # Яндекс
    "15478",   # VK
    "2180",    # Ozon
    "3529",    # Сбер
    "78638",   # Т-Банк
    "84585",   # Авито
    "51775",   # Lamoda
    "1057",    # Лаборатория Касперского
    "3776",    # МТС
    "87021",   # Самокат
]

# Дополнительные компании для режима загрузки из файла (всего 10 компаний в БД).
FALLBACK_COMPANIES = [
    {"company_id": "1006", "company_name": "Авито", "company_url": "https://hh.ru/employer/84585"},
    {"company_id": "1007", "company_name": "Lamoda", "company_url": "https://hh.ru/employer/51775"},
    {"company_id": "1008", "company_name": "Лаборатория Касперского", "company_url": "https://hh.ru/employer/1057"},
    {"company_id": "1009", "company_name": "МТС", "company_url": "https://hh.ru/employer/3776"},
    {"company_id": "1010", "company_name": "Самокат", "company_url": "https://hh.ru/employer/87021"},
]
