# orderflow-backend
Проект для реализации backend логики и REST API.

# установка зависимостей
pip install -r requirements.txt

# запуск приложения
## локальный запуск
fastapi dev app/main.py
## запуск напрямую
uvicorn app.main:app --reload

# запуск тестов
python -m pytest

# проверка стандартов написания кода
ruff check .

# сборка и запуск контейнера Docker
docker build -t orderflow-backend .
docker run --rm -p 8000:8000 orderflow-backend

# проверка запуска Docker
curl http://localhost:8000/health

# запуск приложения и PostgreSQL через Docker Compose
docker compose up --build
# запуск в фоновом режиме
docker compose up --build -d
# остановка контейнеров
docker compose down
# проверка конфигурации Compose:
docker compose config

# DATABASE_URL
## для локального запуска с Mac:
DATABASE_URL=postgresql+psycopg://orderflow:orderflow_password@localhost:55432/orderflow
## для приложения внутри Docker Compose:
DATABASE_URL=postgresql+psycopg://orderflow:orderflow_password@db:5432/orderflow

Внутри Compose приложение обращается к PostgreSQL по имени сервиса 'db' и внутреннему порту '5432' - 'db:5432'.
С Mac подключение идет через опубликованный порт 'localhost:55432'.

