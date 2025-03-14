from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017")
db = client["taskdb"]
tasks_collection = db["tasks"]

tasks_collection.create_index("goal_id") 
tasks_collection.create_index("assignee_id")