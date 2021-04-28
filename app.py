from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import pymongo, json, string, random, os


app = Flask(__name__)
api = Api(app)

URL = os.getenv("DB_URL")
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


class UpdateDeleteBug(Resource):
    def put(self, bug_id):
        client[project]["bug"].update_one({"bug_id" : bug_id},{"$set" : request.form}) 
        return {"message":"succeed"}, 200

    def delete(self, bug_id):
        client[project]["bug"].delete_one({"bug_id":bug_id})
        return {"message":"succeed"}, 200

class Connection(Resource):
    def get(self):
        return {"web":"started", "DB_URL":URL}

api.add_resource(Bug, "/bug/<string:user_id>")
api.add_resource(UpdateDeleteBug, "/bug/ud/<string:bug_id>")
api.add_resource(Connection, "/")

if __name__ == "__main__":
    app.run(debug=False)
