from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from model import Item
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import jwt

import simplejson as json

google_request = requests.Request()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)


@app.route("/")
def index():
    return json.dumps({"items": [item.tiny() for item in Item.query.filter_by(repository_id=2).all()]})


@app.route("/<int:item_id>")
def get_item(item_id):
    return json.dumps(Item.query.filter(Item.id == item_id).one().full())


@app.route("/login", methods=["POST"])
def login():
    print(dir(request))
    as_json = request.get_json()
    print(as_json)
    id_info = id_token.verify_oauth2_token(as_json.get("tokenId"), google_request, 'docentapp.com')
    claims = jwt.decode(as_json.get("tokenId"), verify=False)
    print("-----")
    print(id_info)
    print("%%%%%%%%%%")
    print(claims)
    print("-----")
    return json.dumps(request.args)

# print("HERE:{}".format(os.environ['PORT']))
# app.run(port=int(os.environ.get('PORT', 17995)))


db.create_all()
