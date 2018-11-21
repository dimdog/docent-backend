from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from model import Item

import simplejson as json

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wake@localhost/docent'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)


@app.route("/")
def index():
    return json.dumps({"items": [item.tiny() for item in Item.query.all()]})


@app.route("/<int:item_id>")
def get_item(item_id):
    return json.dumps(Item.query.filter(Item.id == item_id).one().full())

print("HEREEEE")
app.run(port=int(os.environ['PORT']))
