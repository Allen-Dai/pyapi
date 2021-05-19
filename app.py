from flask import Flask, request, Response
from flask_restful import Api, Resource, reqparse
import pymongo, json, string, random, os, datetime, jwt



app = Flask(__name__)
api = Api(app)
URL = "mongodb://"+os.getenv("DB_URL")+":27017"
client = pymongo.MongoClient(URL)
project = os.getenv("PROJECT")

ACAO = {"Access-Control-Allow-Origin":"*"}


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
        
        #Incoming password should be encrypted by client

        user = {"username":request.args.get("username"),"password":request.args.get("password")}


        try:
            username = user["username"]
            password = user["password"]
            if (len(username) == 0 or len(password) == 0):
                return {"message":"Invalid inputs"}, 400, ACAO
        except:
            return {"message":"Invalid inputs"}, 400, ACAO

        cursor = client[project]["user"].find_one(user)

        if cursor==None:
            return {"body":"Invalid username/password"}, 200, ACAO



        access_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=5),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("ACCESS_SECRET"), 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256").decode("utf-8")

        refresh_token = jwt.encode(
                {"exp": datetime.datetime.utcnow()+datetime.timedelta(days=7),
                 "iat": datetime.datetime.utcnow()},
                os.getenv("REFRESH_SECRET")+user["password"], 
                headers = {"alg": "HS256", "typ": "JWT"},
                algorithm="HS256").decode("utf-8")


        resp =  Response()
        resp.headers.add("Access-Control-Allow-Origin","*")
        resp.set_cookie("Access_Token", value = access_token, httponly = True, path = "/")
        resp.set_cookie("Refresh_Token", value = refresh_token, httponly = True, path = "/")

        return resp

        #return {"message":"ok", "access_token":access_token.decode("utf-8"), "refresh_token":refresh_token.decode("utf-8")}, 200, ACAO


class RefreshService(Resource):
    def post(self):
        # NOT FIXED, token should be taken from Auth Bearer header
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
        user = {"username":request.args.get("username"), "password":request.args.get("password")}

        if len(user)>2:
            return {"message":"Bad request"}, 400, ACAO

        try:
            username = user["username"]
            password = user["password"]
        except:
            return {"message":"Bad request"}, 400, ACAO

        if (client[project]["user"].find({"username":user["username"]})).count() > 0:
            return {"message":"Username Unavailble"}, 200, ACAO

        client[project]["user"].insert_one(user)
        return {"message":"Registered"}, 200, ACAO


api.add_resource(Bug, "/bug")
api.add_resource(Login, "/login")
api.add_resource(RefreshService, "/refreshservice")
api.add_resource(Register, "/register")

if __name__ == "__main__":
    app.run(debug=True)
