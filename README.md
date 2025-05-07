# Проект по обнаружению спама (Spam Shield)

Многофункциональный сервис для классификации текстовых запросов (спам/не спам) с интегрированной системой биллинга

## Основные возможности

- **3 уровня моделей**:
  - **Basic**: Правила на ключевых словах
  - **Medium**: Дообученная TF-IDF + Random Forest
  - **Premium**: Облегчённая дообученная версия BERT (DistilBERT)
- **Биллинг-система**:
  - Начальный баланс: 1000 кредитов
  - Стоимость запросов: 100/250/500 кредитов за уровень
  - Пополнение баланса
- **Аналитика**:
  - История запросов
  - Статистика использования
  - Отслеживание расходов

## Настройка проекта

1. Все зависимости были установлены при помощи Poetry. Чтобы их установить, выполните следуюбщую команду:
```bash
poetry install
```

2. Создайте файл .env в корне проекта:
```env
DATABASE_URL = "postgresql://your_user:your_password@localhost:5432/your_db_name" - URL подключения к БД
SECRET_KEY=your_secret_key - секретный ключ для подписи JWT
```

3. Запустите приложение:
```
uvicorn main:app --reload
```

## Эндпоинты API

- POST /register - регистрация нового пользователя
- POST /token - авторизация (получение JWT)
- GET /balance - проверка баланса
- POST /add_credits - пополнение баланса
- POST /predict - анализ текста
- GET /prediction_history - история запросов

## Структура проекта

```
spam_ml/
├── db/                   # Работа с БД
│   ├── data/             # Данные для БД
│   │   └── spam.csv
│   ├── database.py       # Функции работы с БД
│   ├── models.py         # SQLAlchemy модели
│   └── schemas.py        # Pydantic схемы
│
├── ml_models/            # ML-компоненты
│   ├── models/           # Реализация моделей
│   │   ├── basic_model.py
│   │   ├── medium_model.py
│   │   └── premium_model.py
│   ├── models_data/      # Веса моделей
│   │   ├── premium_spam_model/
│   │   ├── medium_model.joblib
│   │   └── tfidf_vectorizer.joblib
│   └── train/            # Обучение моделей
│       ├── train_medium_model.py
│       └── train_premium_model.py
│
├── frontend/             # Веб-интерфейс
│   ├── static/           # CSS/JS
│   │   ├── app.js
│   │   └── styles.css
│   └── templates/        # HTML шаблоны
│       └── index.html
│
├── .gitignore
├── demo.mp4
└── main.py
```

## Стек

**Бэкенд** - FastAPI, SQLAlchemy, JWT

**ML-модели** - Scikit-learn, Transformers, PyTorch

**Базы данных** - PostgreSQL

**Инфраструктура** - Pydantic, Uvicorn, Poetry

## Интерфейс

Интерфейс до авторизации

![Схема](./before.png)

Интерфейс после авторизации

![Схема](./after.png)

## Демо

[Демо проекта](./demo.mp4)
