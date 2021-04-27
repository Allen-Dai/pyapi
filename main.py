from flask import Flask, request
from flask_restful import Api, Resource, reqparse
import pymongo, json, string, random
import loadenv

client = pymongo.MongoClient(loadenv._get("DB_URL"))
project = loadenv._get("PROJECT")


app = Flask(__name__)
api = Api(app)




class Bug(Resource):
        
    def get(self,user_id):
        cursor = client[project]["bug"].find({"user_id":user_id},{"_id": False})
        bugs = []
        for bug in cursor:
            bugs.append(bug)

        if bugs == []:
            return 204
        return bugs

    def put(self, user_id):
        try:
            bug_id = request.form["bug_id"]
            update_content = json.loads(request.form["update"])

            
            client[project]["bug"].update_one({"bug_id" : bug_id},{"$set" : update_content}) 
        except:
            return {"message":"Errors"}, 404

    def post(self, user_id):
        data = json.loads(request.form["create"])
        data["bug_id"] = (''.join(random.choice(string.ascii_letters + string.digits) for _ in range(40)))
        client[project]["bug"].insert_one(data)
        return {"message":"succeed"}, 200


class DeleteBug(Resource):
    def delete(self, bug_id):
        client[project]["bug"].delete_one({"bug_id":bug_id})
        return {"message":"succeed"}, 200


    
        

api.add_resource(Bug, "/bug/<string:user_id>")

api.add_resource(DeleteBug, "/bug/delete/<string:bug_id>")

if __name__ == "__main__":
    app.run(debug=True, port=8080)

