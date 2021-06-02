from fastapi import FastAPI
from dotenv import load_dotenv
from model import Bug

import uvicorn, pymongo, os, json, hashlib

load_dotenv()
URL = os.getenv("DB_URL")
DB = os.getenv("PROJECT")
client = pymongo.MongoClient(URL)

app = FastAPI()

@app.get("/")
async def index():
    return {"message":"Welcome"}


@app.get("/bug/user/{from_user}")
async def get_user_bugs(from_user: str):
    cursor = client[DB]["bug"].find({"from_user": from_user}, {"_id": False})
    bugs = []
    for bug in cursor:
       bugs.append(bug)
    return bugs

@app.get("/bug/{bug_id}")
async def get_bug(bug_id: int):
    bug = client[DB]["bug"].find_one({"id": bug_id}, {"_id": False})
    return bug


@app.post("/bug/")
async def create_bug(bug: Bug):
    client[DB]["bug"].insert_one(bug.dict())
    return bug 


#@app.post("/user/register/")
#async def create_user(user: User):
#    user.password = hashlib.sha256(user.password.encode("utf-8")).hexdigest()
#    client[DB]["user"].insert_one(user.dict())
#    return user


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
