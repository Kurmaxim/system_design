import pika
import json

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Создание очереди (если она не существует)
channel.queue_declare(queue='user_queue')

# Функция для обработки сообщений
def callback(ch, method, properties, body):
    user_data = json.loads(body)
    print(f" [x] Received user data: {user_data}")

# Установка функции обратного вызова для получения сообщений
channel.basic_consume(queue='user_queue',
                      on_message_callback=callback,
                      auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Запуск цикла получения сообщений
channel.start_consuming()