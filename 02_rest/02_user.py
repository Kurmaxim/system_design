from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Модель данных для пользователя
class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

# Временное хранилище для пользователей
users_db = []

# GET /users - Получить всех пользователей
@app.get("/users", response_model=List[User])
def get_users():
    return users_db

# GET /users/{user_id} - Получить пользователя по ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# POST /users - Создать нового пользователя
@app.post("/users", response_model=User)
def create_user(user: User):
    users_db.append(user)
    return user

# PUT /users/{user_id} - Обновить пользователя по ID
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# DELETE /users/{user_id} - Удалить пользователя по ID
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            deleted_user = users_db.pop(index)
            return deleted_user
    raise HTTPException(status_code=404, detail="User not found")

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)