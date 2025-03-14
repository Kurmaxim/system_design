from mongo import tasks_collection

def clear_mongo():
    tasks_collection.delete_many({})
    print("Все данные из MongoDB удалены.")

if __name__ == "__main__":
    clear_mongo()