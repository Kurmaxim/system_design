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

class Transaction(BaseModel):
    id: int
    user: User
    status : int # 0 -created, 1- commited , 2 - aborted



# Временное хранилище для пользователей
users_db = {}
transactions =  {}
max_transaction = 1



# GET /users/{user_id} - Получить пользователя по ID
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    if user_id in transactions:
        tr = transactions[user_id]
        if tr.status == 1:
            print(f'applay transaction {tr.id}')
            users_db[user_id] = tr.user
            transactions.pop(user_id,None)
        elif tr.status == 2:
            print(f'erase transaction {tr.id}')
            transactions.pop(user_id,None)

    if user_id in users_db:
        return users_db[user_id]
    raise HTTPException(status_code=404, detail="User not found")

# GET /users - Получить всех пользователей
@app.get("/users", response_model=List[User])
def get_users():
    to_remove = list()
    for tr in transactions.values():
        if tr.status == 1:
            users_db[tr.user.id] = tr.user
            print(f'applay transaction {tr.id}')
            to_remove.append(tr.user.id)
    for id in to_remove:
        transactions.pop(id,None)

    return [user for user in users_db.values()]

# POST /users - Создать нового пользователя
@app.post("/users", response_model=Transaction)
def create_user(user: User):
    if user.id in users_db:
        raise HTTPException(status_code=404, detail="User already exist")

    if user.id in transactions:
        tr = transactions[user.id]
        if tr.status == 1: #commited
            users_db[tr.user.id] = tr.user
            transactions.pop(tr.user.id,None)
            print(f'applay transaction {tr.id}')
        elif tr.status == 0: # created
            raise HTTPException(status_code=404, detail="You have uncommited transaction") 
        else: # aborted
            print(f'erase transaction {tr.id}')
            transactions.pop(tr.user.id,None)
    global max_transaction
    
    tr = Transaction(id = max_transaction,user = user, status =0)
    max_transaction = max_transaction+1
    transactions[user.id] = tr
    print(f'add transaction {tr.id}')
    return tr

@app.post("/tx/{id}/{status}",response_model = Transaction)
def change_transaction(id:int, status:int):
    print(f'transactions: {transactions}')
    user_id = None
    for tr in transactions.values():
        if tr.id == id:
            user_id = tr.user.id

    if not user_id is None:
        tr = transactions[user_id]

        if status == 1:
            if tr.status == 0:
                print(f'transaction {id} commited')
                tr.status = 1
                return tr
            else:
                raise HTTPException(status_code=404, detail="Can't commit transaction") 
        elif status == 2:
            if tr.status == 0:
                print(f'transaction {id} aborted')
                tr.status = 2
                return tr
            else:
                raise HTTPException(status_code=404, detail="Can't commit transaction") 
        else:
            raise HTTPException(status_code=404, detail="Unsupported status") 
    else:
        raise HTTPException(status_code=404, detail="Transaction not found") 


# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)