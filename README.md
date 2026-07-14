# orderflow-backend

Проект для реализации backend-логики и REST API.

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Локальный запуск приложения

```bash
fastapi dev app/main.py
```

Альтернативный запуск:

```bash
uvicorn app.main:app --reload
```

Для локального запуска приложению нужен `DATABASE_URL`, например:

```text
DATABASE_URL=postgresql+psycopg://orderflow:orderflow_password@localhost:55432/orderflow
```

## Тесты

```bash
python -m pytest
```

## Проверка качества кода

```bash
ruff check .
```

## Docker

Сборка образа:

```bash
docker build -t orderflow-backend .
```

Запуск только app-контейнера возможен только при доступной базе данных и переданном `DATABASE_URL`.

Основной способ запуска приложения вместе с PostgreSQL:

```bash
docker compose up --build
```

Запуск в фоновом режиме:

```bash
docker compose up --build -d
```

Остановка контейнеров:

```bash
docker compose down
```

Остановка контейнеров с удалением volume БД:

```bash
docker compose down -v
```

`docker compose down -v` удаляет данные PostgreSQL. Это разрушительная команда.

Проверка конфигурации Compose:

```bash
docker compose config
```

## Проверка приложения

```bash
curl http://localhost:8000/health
```

Создание order:

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"title": "First API order"}'
```

Получение order по id:

```bash
curl http://localhost:8000/orders/1
```

Получение списка orders:

```bash
curl http://localhost:8000/orders
```

## DATABASE_URL

Для локального запуска с Mac:

```text
DATABASE_URL=postgresql+psycopg://orderflow:orderflow_password@localhost:55432/orderflow
```

Для приложения внутри Docker Compose:

```text
DATABASE_URL=postgresql+psycopg://orderflow:orderflow_password@db:5432/orderflow
```

Внутри Compose приложение обращается к PostgreSQL по имени сервиса `db` и внутреннему порту `5432`: `db:5432`.

С Mac подключение идёт через опубликованный порт `localhost:55432`.

## Alembic

Проверить текущую revision БД:

```bash
python -m alembic current
```

Применить миграции:

```bash
python -m alembic upgrade head
```

Создать новую migration после изменения ORM-моделей:

```bash
python -m alembic revision --autogenerate -m "message"
```

## Структура проекта

### `app/api/routes/orders.py`

FastAPI endpoints для orders:

* `POST /orders` — создать новый order;
* `GET /orders/{order_id}` — получить order по id;
* `GET /orders` — получить список orders.

### `app/schemas/order.py`

Pydantic-схемы:

* `OrderCreate` — данные, которые клиент может отправить для создания order;
* `OrderRead` — данные об order, которые API возвращает клиенту.

### `tests/test_orders_api.py`

API-тесты для orders endpoints:

* создание order;
* получение существующего order;
* получение отсутствующего order;
* получение списка orders.
