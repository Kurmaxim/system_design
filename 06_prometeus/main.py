from fastapi import FastAPI, Request, Response
from prometheus_client import start_http_server, Counter, Histogram
import time

# Создаем экземпляр FastAPI
app = FastAPI()

# Создаем счетчик для подсчета количества запросов
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])

# Создаем гистограмму для измерения latency
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])

# Запускаем сервер для экспорта метрик на порту 9100
start_http_server(9100)

# Middleware для отслеживания запросов и измерения latency
@app.middleware("http")
async def track_request_data(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    # Увеличиваем счетчик запросов
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    # Измеряем latency
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Записываем latency в гистограмму
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)

    return response

# Пример эндпоинта
@app.get("/hello")
async def hello():
    time.sleep(0.1)  # Имитация задержки
    return {"message": "Hello, World!"}

# Пример эндпоинта
@app.get("/goodbye")
async def goodbye():
    time.sleep(0.2)  # Имитация задержки
    return {"message": "Goodbye, World!"}

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)