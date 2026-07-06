import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://orderflow:orderflow_password@localhost:55432/orderflow",
)
