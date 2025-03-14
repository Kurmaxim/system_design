from database import SessionLocal, User, Goal
from passlib.context import CryptContext
from mongo import tasks_collection
import logging
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    db = SessionLocal()

    try:
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": pwd_context.hash("secret"),
                "first_name": "Admin",
                "last_name": "User",
                "age": 30
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "hashed_password": pwd_context.hash("password1"),
                "first_name": "John",
                "last_name": "Doe",
                "age": 25
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "hashed_password": pwd_context.hash("password2"),
                "first_name": "Jane",
                "last_name": "Smith",
                "age": 28
            }
        ]

        user_ids = {} 

        for user_data in users_data:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(**user_data)
                db.add(user)
                db.commit()
                db.refresh(user)
                user_ids[user_data["username"]] = user.id 
        logger.info("Пользователи добавлены в базу.")

        admin_user = db.query(User).filter(User.username == "admin").first()

        goals_data = [
            {
                "id": "goal1",
                "description": "Learn FastAPI",
                "owner_id": admin_user.id
            },
            {
                "id": "goal2",
                "description": "Build a REST API",
                "owner_id": admin_user.id
            },
            {
                "id": "goal3",
                "description": "Deploy a microservice",
                "owner_id": admin_user.id
            }
        ]

        for goal_data in goals_data:
            existing_goal = db.query(Goal).filter(Goal.id == goal_data["id"]).first()
            if not existing_goal:
                goal = Goal(**goal_data)
                db.add(goal)
        db.commit()
        logger.info("Цели добавлены в базу.")

        # Инициализация задач в MongoDB
        tasks_data = [
            {
                "description": "Read FastAPI documentation",
                "goal_id": "goal1",
                "assignee_id": user_ids["user1"],
                "status": "pending"
            },
            {
                "description": "Create a simple FastAPI app",
                "goal_id": "goal1",
                "assignee_id": user_ids["user2"],
                "status": "pending"
            },
            {
                "description": "Design API endpoints",
                "goal_id": "goal2",
                "assignee_id": user_ids["user1"],
                "status": "pending"
            },
            {
                "description": "Implement CRUD operations",
                "goal_id": "goal2",
                "assignee_id": user_ids["user2"],
                "status": "pending"
            },
            {
                "description": "Deploy app to Heroku",
                "goal_id": "goal3",
                "assignee_id": user_ids["admin"],
                "status": "pending"
            }
        ]

        for task_data in tasks_data:
            existing_task = tasks_collection.find_one({
                "description": task_data["description"],
                "goal_id": task_data["goal_id"],
                "assignee_id": task_data["assignee_id"]
            })
            if not existing_task:
                tasks_collection.insert_one(task_data)
        logger.info("Задачи добавлены в MongoDB.")

    except Exception as e:
        logger.error(f"Ошибка при добавлении данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()