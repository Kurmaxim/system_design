from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from circuit_breaker import CircuitBreaker
from user_service import User
import requests

app = FastAPI()

# Модель данных для пользователя
class Order(BaseModel):
    id: int
    name: str
    user_id: int
    user : Optional[User] = Field(None, description="Order user")

# Временное хранилище для пользователей
orders_db = []
breaker   = CircuitBreaker()

# GET /users - Получить всех пользователей
@app.get("/orders", response_model=List[Order])
def get_orders():
    return orders_db

# GET /users/{user_id} - Получить пользователя по ID
@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    for order in orders_db:
        if order.id == order_id:
            # try to load user
            if breaker.check('users'):
                response = None
                try:
                    url = f"http://localhost:8001/users/{order.user_id}"
                    headers = {'content-type': 'application/json', 'accept': 'application/json'}
                    response = requests.get(url = url ,headers=headers)
                except:
                    breaker.fail('users')
                    raise HTTPException(status_code=404, detail="Users not available")
                
                if (response is not None) and (response.status_code == 200):
                    breaker.success('users')
                    user = response.json()
                    order.user = User(**user)
                    return order
                else:
                    breaker.fail('users')
                    raise HTTPException(status_code=404, detail="Users not available")
            else:
                print(f"Skip requets to users server")
                raise HTTPException(status_code=404, detail="Users not available")
                    
    raise HTTPException(status_code=404, detail="Order not found")

# POST /users - Создать нового пользователя
@app.post("/orders", response_model=Order)
def create_order(order: Order):
    for o in orders_db:
        if o.id == order.id:
            raise HTTPException(status_code=404, detail="User already exist")
    orders_db.append(order)
    return order

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)