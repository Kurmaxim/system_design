from sqlalchemy import MetaData, create_engine
from database import engine

def drop_tables():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    print("Все таблицы PostgreSQL удалены.")

if __name__ == "__main__":
    drop_tables()