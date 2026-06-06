# Проект 3. Поиск вакансий с подключением БД

Проект получает данные о работодателях и вакансиях с [API hh.ru](https://api.hh.ru/openapi/redoc), сохраняет их в PostgreSQL и предоставляет интерфейс для анализа через класс `DBManager`.

## Возможности

- Получение данных о 10 компаниях и их вакансиях через API hh.ru
- Автоматическое создание базы данных и таблиц PostgreSQL
- Резервная загрузка из файла `data/hh_vacancies_sample.json`, если API недоступен
- Консольное меню для просмотра компаний, вакансий и зарплат

## Структура проекта

```
.
├── api_hh.py          # взаимодействие с API hh.ru
├── file_manager.py    # чтение подготовленных данных из файла
├── vacancies.py       # обработка и подготовка вакансий
├── database.py        # создание БД и загрузка данных
├── db_manager.py      # класс DBManager
├── config.py          # конфигурация и список компаний
├── main.py            # точка входа
├── data/
│   └── hh_vacancies_sample.json
├── requirements.txt
└── .env.example
```

## Требования

- Python 3.11+
- PostgreSQL 14+

## Установка

1. Клонируйте репозиторий:

```bash
git clone <url-репозитория>
cd hh-vacancies-db
```

2. Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Скопируйте файл окружения и укажите доступ к PostgreSQL:

```bash
copy .env.example .env
```

Пример `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=hh_vacancies
```

## Запуск

```bash
python main.py
```

При запуске программа:

1. Создает базу данных `hh_vacancies`, если она отсутствует
2. Создает таблицы `companies` и `vacancies`
3. Загружает данные через API hh.ru или из файла-заглушки
4. Открывает консольное меню

## Класс DBManager

Реализованные методы:

- `get_companies_and_vacancies_count()` — компании и количество вакансий
- `get_all_vacancies()` — все вакансии с компанией, зарплатой и ссылкой
- `get_avg_salary()` — средняя зарплата
- `get_vacancies_with_higher_salary()` — вакансии выше средней зарплаты
- `get_vacancies_with_keyword(keyword)` — поиск вакансий по ключевому слову

## Используемые API

- Работодатели: `https://api.hh.ru/employers/{employer_id}`
- Вакансии: `https://api.hh.ru/vacancies?employer_id={employer_id}`

## Автор

Учебный проект по работе с PostgreSQL и API hh.ru.
