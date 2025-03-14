import json
from confluent_kafka import Consumer, KafkaError
from database import SessionLocal, User
from sqlalchemy.exc import IntegrityError

KAFKA_TOPIC = 'user_created'

def get_kafka_consumer():
    return Consumer({
        'bootstrap.servers': 'kafka1:9092,kafka2:9092',
        'group.id': 'user_consumer_group',
        'auto.offset.reset': 'earliest'
    })

def process_user_message(message):
    db = SessionLocal()
    try:
        user_data = json.loads(message.value())
        existing_user = db.query(User).filter(
            (User.username == user_data["username"]) | (User.email == user_data["email"])
        ).first()
        if existing_user:
            print(f"Пользователь с username={user_data['username']} или email={user_data['email']} уже существует. Пропускаем.")
            return

        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=user_data["hashed_password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            age=user_data["age"]
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Пользователь {user.username} создан и сохранен в базе данных. ID: {user.id}")
    except IntegrityError as e:
        db.rollback()
        print(f"Ошибка IntegrityError при обработке сообщения: {e}")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при обработке сообщения: {e}")
    finally:
        db.close()

def consume_messages():
    consumer = get_kafka_consumer()
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Ошибка Kafka: {msg.error()}")
                    break
            process_user_message(msg)
    except KeyboardInterrupt:
        print("Остановка Kafka...")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages()