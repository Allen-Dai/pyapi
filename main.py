from flask import Flask, request
from flask_restful import Api, Resource 
import pymongo, loadenv, json

client = pymongo.MongoClient(loadenv._get("DB_URL"))
project = loadenv._get("PROJECT")


app = Flask(__name__)
api = Api(app)





class Bug(Resource):
        
    def get(self,user):
        cursor = client[project]["bug"].find({"user":user},{"_id": False})
        bugs = []
        for bug in cursor:
            bugs.append(bug)
        return bugs

    def put(self, user):
        try:
            bug_id = int(request.form["bug_id"])
            update_content = json.loads(request.form["update"])

            
            client[project]["bug"].update_one({"bug_id" : bug_id},{"$set" : update_content}) 
        except:
            return {"message":"Errors"}

        

    
        

api.add_resource(Bug, "/bug/<int:user>")

if __name__ == "__main__":
    app.run(debug=True, port=8080)

