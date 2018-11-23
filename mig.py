from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from model import Item, Artist, Repository, Department


app = Flask(__name__)

print(os.environ)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
print app.config['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(app)


db.create_all()

first_item = Item.query.first()
rep_dict = {"name": first_item.repository,
            "city": "New York",
            "state": "NY",
            "country": "United States of America"}
rep = Repository(**rep_dict)
db.session.add(rep)
db.session.commit()
