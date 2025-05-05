from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Настройка логирования
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Используем ваши данные
DATABASE_URL = "postgresql://api_user:admin@localhost:5432/spam_db"

Base = declarative_base()

# Создаём engine с явным указанием клиентской кодировки
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"options": "-c client_encoding=utf8"}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)
SessionLocal.configure(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
