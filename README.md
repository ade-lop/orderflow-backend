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
pytest -m pytest

# проверка стандартов написания кода
ruff check .
