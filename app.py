from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from models import User, Activity, Scan

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

api = Api(app)
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)