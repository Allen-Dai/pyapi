from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import pymongo, json, string, random, os


app = Flask(__name__)
api = Api(app)

URL = "mongodb://"+os.getenv("DB_URL")+":27017"
client = pymongo.MongoClient(URL)
project = os.getenv("PROJECT")

class Bug(Resource):
        
    def get(self,user_id):
        cursor = client[project]["bug"].find({"user_id":user_id},{"_id": False})
        bugs = []
        for bug in cursor:
            bugs.append(bug)

        if bugs == []:
            return 204
        return bugs, 200


    def post(self, user_id):
        data = request.form.to_dict()
        data["bug_id"] = (''.join(random.choice(string.ascii_letters + string.digits) for _ in range(40)))
        client[project]["bug"].insert_one(data)
        return {"message":"succeed"}, 200


    def put(self, bug_id):
        client[project]["bug"].update_one({"bug_id" : bug_id},{"$set" : request.form}) 
        return {"message":"succeed"}, 200

    def delete(self, bug_id):
        client[project]["bug"].delete_one({"bug_id":bug_id})
        return {"message":"succeed"}, 200

class Login(Resource):
    def get(self):
        username = request.args.get("username")
        password = request.args.get("password")
        if (username==None or password==None):
            return {"message":"Invalid input"}, 400

        cursor = client[project]["user"].find_one({"username":username, "password":password})
        if cursor.count()==0:
            return {"message":"Invalid username/password"}, 200


        return {"message":"OK"}, 200

    def post(self):
        username = request.args.get("username")
        password = request.args.get("password")

        user = {"username":username, "password":password}
        client[project]["user"].insert_one(user)
        
        return {"message":"Registered"}, 200




        

api.add_resource(Bug, "/bug")
api.add_resource(Login, "/login")

if __name__ == "__main__":
    app.run(debug=False)
