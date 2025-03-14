from database import engine, Base

def drop_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        print("Все таблицы удалены.")
    except Exception as e:
        print(f"Ошибка при удалении таблиц: {e}")

if __name__ == "__main__":
    drop_tables()