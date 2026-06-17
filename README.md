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
docker compose up --buid -d
# остановка контейнероа
docker compose down

