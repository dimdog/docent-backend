from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from model import Item, User
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_login import LoginManager, login_user, current_user

import simplejson as json

google_request = requests.Request()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.environ["FLASK_SECRET_KEY"]


@login_manager.user_loader
def load_user(user_id):
    return User.get(session["user_id"])


@app.route("/")
def index():
    return json.dumps({"items": [item.tiny() for item in Item.query.filter_by(repository_id=2).all()]})


@app.route("/<int:item_id>")
def get_item(item_id):
    print(current_user)
    return json.dumps(Item.query.filter(Item.id == item_id).one().full())


@app.route("/login", methods=["POST"])
def login():
    as_json = request.get_json()
    # TODO THIS DOES NOT FEEL SECURE!
    print("%%%%%%%%%%")
    id_info = id_token.verify_oauth2_token(as_json.get("tokenId"), google_request, audience='633799705698-fs81n284e1iv4318fk2vdclksv29d82e.apps.googleusercontent.com')
    print(id_info)
    print("-----")
    if "iss" in id_info and id_info["iss"] == "accounts.google.com" \
            and as_json["email"] == id_info["email"]:
        user = User.query.filter_by(email=as_json["email"]).first()
        if user:
            print("Found user:{}").format(user.to_json())
        if not user:
            user = User(family_name=id_info["family_name"], given_name=id_info["given_name"], full_name=id_info["name"],
                        image_url=id_info["picture"], email=as_json["email"], locale=id_info["locale"])
            db.session.add(user)
            db.session.commit()
        login_user(user)
        print(session)
        session['user_id'] = user.id
    return json.dumps(user.to_json())
# {'iss': 'accounts.google.com', 'azp': '633799705698-fs81n284e1iv4318fk2vdclksv29d82e.apps.googleusercontent.com', 'aud': '633799705698-fs81n284e1iv4318fk2vdclksv29d82e.apps.googleusercontent.com', 'sub': '101477866356937362560', 'email': 'dimdog@gmail.com', 'email_verified': True, 'at_hash': 'FrCen2m7wpa-WwTxfWta0g', 'name': 'Ben Reiter', 'picture': 'https://lh6.googleusercontent.com/-37vcW9X8k70/AAAAAAAAAAI/AAAAAAAADy8/oqM2ebjWLxQ/s96-c/photo.jpg', 'given_name': 'Ben', 'family_name': 'Reiter', 'locale': 'en', 'iat': 1543177052, 'exp': 1543180652, 'jti': 'db71a5490749bf79be98b9f685d7dc223159c6d4'}

# print("HERE:{}".format(os.environ['PORT']))
# app.run(port=int(os.environ.get('PORT', 17995)))


db.create_all()
