from fastapi import FastAPI
from dotenv import load_dotenv
from model import Bug

import pymongo, os, json

load_dotenv()
URL = os.getenv("DB_URL")
DB = os.getenv("PROJECT")
client = pymongo.MongoClient(URL)

app = FastAPI()

@app.get("/")
def index():
    return {"message":"Welcome"}


@app.get("/bug/user/{from_user}")
def get_user_bugs(from_user: str):
    cursor = client[DB]["bug"].find({"from_user": from_user}, {"_id": False})
    bugs = []
    for bug in cursor:
       bugs.append(bug)
    return bugs

@app.get("/bug/{bug_id}")
def get_bug(bug_id: int):
    bug = client[DB]["bug"].find_one({"id": bug_id}, {"_id": False})
    return bug


@app.post("/bug/")
def create_bug(bug: Bug):
    client[DB]["bug"].insert_one(bug.dict())
    return bug 

