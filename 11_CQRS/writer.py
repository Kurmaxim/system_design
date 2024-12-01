from confluent_kafka import Consumer, KafkaError
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import json


# Настройка SQLAlchemy
DATABASE_URL = "postgresql://stud:stud@db/archdb"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

class UserCreate(BaseModel):
    first_name: str
    last_name: str

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Конфигурация Kafka Consumer
conf = {
    'bootstrap.servers': 'kafka1:9092,kafka2:9092',  # Адрес Kafka брокера
    'group.id': 'user_group',  # ID группы потребителей
    'auto.offset.reset': 'earliest'  # Начинать с самого раннего сообщения
}

# Создание Consumer
consumer = Consumer(conf)

# Подписка на топик
consumer.subscribe(['user_topic'])

# Цикл для получения сообщений
db = SessionLocal()
try:
    while True:
        msg = consumer.poll(1.0)  # Ожидание сообщения в течение 1 секунды

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        # Десериализация JSON и вывод на экран
        user_data = json.loads(msg.value().decode('utf-8'))
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        print(f"Received user data: {user_data}")

except KeyboardInterrupt:
    pass

finally:
    # Закрытие Consumer
    consumer.close()
    db.close()