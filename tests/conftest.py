import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://user:password@localhost:55432/orderflow",
)
