from flask import Flask
from flask_restful import Resource
import pymongo, loadenv

client = pymongo.MongoClient(loadenv._get("DB_URL"))


