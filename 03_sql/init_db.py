from database import SessionLocal, User, Goal, Task
from passlib.context import CryptContext
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    db = SessionLocal()

    try:
        users = [
            User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("secret"),
                first_name="Admin",
                last_name="User",
                age=30
            ),
            User(
                username="user1",
                email="user1@example.com",
                hashed_password=pwd_context.hash("password1"),
                first_name="John",
                last_name="Doe",
                age=25
            ),
            User(
                username="user2",
                email="user2@example.com",
                hashed_password=pwd_context.hash("password2"),
                first_name="Jane",
                last_name="Smith",
                age=28
            )
        ]

        for user in users:
            db.add(user)
        db.commit()
        logger.info("Пользователи добавлены в базу.")

        admin_user = db.query(User).filter(User.username == "admin").first()

        goals = [
            Goal(
                id="goal1",
                description="Learn FastAPI",
                owner_id=admin_user.id 
            ),
            Goal(
                id="goal2",
                description="Build a REST API",
                owner_id=admin_user.id 
            ),
            Goal(
                id="goal3",
                description="Deploy a microservice",
                owner_id=admin_user.id 
            )
        ]

        for goal in goals:
            db.add(goal)
        db.commit()
        logger.info("Цели добавлены в базу.")

        tasks = [
            Task(
                id="task1",
                description="Read FastAPI documentation",
                goal_id=goals[0].id, 
                assignee_id=admin_user.id 
            ),
            Task(
                id="task2",
                description="Create API endpoints",
                goal_id=goals[1].id, 
                assignee_id=users[1].id 
            ),
            Task(
                id="task3",
                description="Write unit tests",
                goal_id=goals[1].id, 
                assignee_id=users[2].id 
            ),
            Task(
                id="task4",
                description="Deploy to Docker",
                goal_id=goals[2].id, 
                assignee_id=admin_user.id 
            )
        ]

        for task in tasks:
            db.add(task)
        db.commit()
        logger.info("Задачи добавлены в базу.")

    except Exception as e:
        logger.error(f"Ошибка при добавлении данных: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()