from flask import Flask, request, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from model import Item, User
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_login import LoginManager, current_user

import simplejson as json

from Crypto.Cipher import AES
aes_obj = AES.new(os.environ["CRYPTO_SEED"], AES.MODE_CBC, os.environ["CRYPTO_IV"])

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
    print("-----------"+user_id+"--------------")
    return User.get(session["user_id"])


@app.route("/")
def index():
    return json.dumps({"items": [item.tiny() for item in Item.query.filter_by(repository_id=2).all()]})


@app.route("/<int:item_id>")
def get_item(item_id):
    print(current_user)
    print(request.cookies)
    print(session)
    return json.dumps(Item.query.filter(Item.id == item_id).one().full())


def load_user_from_token(token, email_verify=None):
    id_info = id_token.verify_oauth2_token(token, google_request, audience='633799705698-fs81n284e1iv4318fk2vdclksv29d82e.apps.googleusercontent.com')
    if "iss" in id_info and id_info["iss"] == "accounts.google.com" \
            and (email_verify is None or email_verify == id_info["email"]):
        db_user = User.query.filter_by(email=email_verify).first()
        if db_user:
            print("Found user:{}".format(db_user.to_json()))
        if not db_user:
            db_user = User(family_name=id_info["family_name"], given_name=id_info["given_name"], full_name=id_info["name"],
                        image_url=id_info["picture"], email=email_verify, locale=id_info["locale"])
            db.session.add(db_user)
            db.session.commit()
    return db_user

@app.route("/login", methods=["POST"])
def login():
    as_json = request.get_json()
    # TODO THIS DOES NOT FEEL SECURE!
    db_user = load_user_from_token(as_json.get("tokenId"), as_json["email"])
    resp = make_response(json.dumps(db_user.to_json()))
    resp.set_cookie("userToken", as_json.get("tokenId"))
    return resp

# print("HERE:{}".format(os.environ['PORT']))
# app.run(port=int(os.environ.get('PORT', 17995)))


db.create_all()
