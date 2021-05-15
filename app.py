from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import pymongo, json, string, random, os, datetime, jwt



app = Flask(__name__)
api = Api(app)
URL = "mongodb://"+os.getenv("DB_URL")+":27017"
client = pymongo.MongoClient(URL)
project = os.getenv("PROJECT")


class Bug(Resource):
        
    def get(self):
        username = request.args.get("username")
        cursor = client[project]["bug"].find({"username":username},{"_id": False})
        
        if cursor.count()==0:
            return {"message":"ok"}, 200

        bugs = []
        for bug in cursor:
            bugs.append(bug)
        #bugs array contains all the bug json object
        return bugs, 200


    def post(self):
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
    def post(self):
        user = request.form.to_dict()

        try:
            username = user["username"]
            password = user["password"]
            if (len(username) == 0 or len(password) == 0):
                return {"message":"Invalid inputs"}, 400
        except:
            return {"message":"Invalid inputs"}, 400

        cursor = client[project]["user"].find(user)

        if cursor.count()==0:
            return {"message":"Invalid username/password"}, 200 
            
        access_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=5),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("ACCESS_SECRET"), 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256")

        refresh_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(days=7),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("REFRESH_SECRET")+user["password"], 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256")

        
        return {"message":"ok", "access":access_token.decode("utf-8"), "refresh":refresh_token.decode("utf-8")}, 200


class RefreshService(Resource):
    def post(self):
        body = request.form.to_dict()
        try:
            refresh_token= body["refresh_token"]
            username = body["username"]
        except:
            return {"message":"Bad request"}, 400

        cursor = client[project]["user"].find_one({"username":username})

        if cursor==None:
            return {"message":"Bad request"}, 400
        password = cursor["password"]

        
        try:
            jwt.decode(refresh_token, os.getenv("REFRESH_SECRET")+password, algorithm="HS256")
        except:
            return {"message":"Token invalid/expired"}, 400

        access_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=5),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("ACCESS_SECRET"), 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256")

        return {"message":"ok", "access_token":access_token}, 200
        


class Register(Resource):

    def post(self):
        user = request.form.to_dict()

        if len(user)>2:
            return {"message":"Bad request"}, 400

        try:
            username = user["username"]
            password = user["password"]
        except:
            return {"message":"Bad request"}, 400

        if (client[project]["user"].find({"username":user["username"]})).count() > 0:
            return {"message":"Username Unavailble"}, 200

        client[project]["user"].insert_one(user)
        return {"message":"Registered"}, 200


api.add_resource(Bug, "/bug")
api.add_resource(Login, "/login")
api.add_resource(RefreshService, "/refreshservice")
api.add_resource(Register, "/register")

if __name__ == "__main__":
    app.run(debug=False)
