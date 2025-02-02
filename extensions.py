from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask("HTN Badge Scanner")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
api = Api(app)
db = SQLAlchemy(app)
