from flask import Flask, request, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import os
from model import Item, User, UserLike, Repository
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_sslify import SSLify
from collections import defaultdict
import random


import simplejson as json

# from Crypto.Cipher import AES
# aes_obj = AES.new(os.environ["CRYPTO_SEED"], AES.MODE_CBC, os.environ["CRYPTO_IV"])

google_request = requests.Request()
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
sslify = SSLify(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).one()


@app.route("/api/random", methods=["GET"])
def random_item():
    random_item = Item.query.order_by(func.random()).limit(1)[0]  # for PostgreSQL, SQLite
    return json.dumps(random_item.full())


@app.route("/api/gallery", methods=["GET"])
@login_required
def gallery():
    repositories = Repository.query.all()
    likes = [like.item for like in current_user.likes.values()]
    items_by_repo = defaultdict(list)
    for item in likes:
        items_by_repo[item.repository_id].append(item)
    response = {"user": current_user.to_json(), "repositories": [repo.to_json(items=items_by_repo[repo.id]) for repo in repositories]}
    return json.dumps(response)


def random_selection(in_list, count):
    if len(in_list) <= count:
        return in_list
    return random.choices(in_list, k=count)


@app.route("/api", methods=["GET"])
def index():
    repository_id = int(request.args.get('repository', '2'))
    repository = Repository.query.filter_by(id=repository_id).one()
    items = [item.tiny() for item in Item.query.filter_by(repository_id=repository_id).all()]
    limited_list = random_selection(items, 100)
    response = {"items": limited_list, "repository": repository.to_json()}
    if not current_user.is_anonymous:
        response['user'] = current_user.to_json()
    return json.dumps(response)


@app.route("/api/like/<int:item_id>", methods=["POST", "DELETE"])
@login_required
def like_item(item_id):
    if request.method == "POST":
        if item_id not in current_user.likes:
            ul = UserLike(user_id=current_user.id, item_id=item_id)
            db.session.add(ul)
            db.session.commit()
    else:
        if item_id in current_user.likes:
            curr_session = db.session.object_session(current_user.likes[item_id])
            curr_session.delete(current_user.likes[item_id])
            curr_session.commit()
    return item_response(current_user, item_id)


def item_response(db_user, item_id):
    item = Item.query.filter(Item.id == item_id).one()   # do better than 500 on error
    response = {"item": item.full(), "repository": item.repository.to_json()}
    if item.artist.name != "anonymous":
        response['artist_other_works'] = [i.tiny() for i in Item.query.filter(Item.id != item_id).filter_by(artist_id=item.artist_id)]
    else:
        response['artist_other_works'] = []
    response['department_other_works'] = [i.tiny() for i in random.choices(Item.query.filter(Item.id != item_id).filter_by(department_id=item.department_id).all(), k=10)]
    if not db_user.is_anonymous:
        response["item"]["liked"] = item_id in db_user.likes
        response["user"] = db_user.to_json()
    return json.dumps(response)


@app.route("/api/<int:item_id>", methods=["GET"])
def get_item(item_id):
    response = item_response(current_user, item_id)
    return response


def load_user_from_request(request):
    as_json = request.get_json()
    # TODO THIS DOES NOT FEEL SECURE!
    db_user = load_user_from_token(as_json.get("tokenId"), as_json.get("email", None))
    return db_user


def load_user_from_token(token, email_verify=None):
    id_info = id_token.verify_oauth2_token(token, google_request, audience='633799705698-fs81n284e1iv4318fk2vdclksv29d82e.apps.googleusercontent.com')
    if "iss" in id_info and id_info["iss"] == "accounts.google.com" \
            and (email_verify is None or email_verify == id_info["email"]):
        db_user = User.query.filter_by(email=id_info["email"]).first()
        if not db_user:
            db_user = User(family_name=id_info["family_name"], given_name=id_info["given_name"], full_name=id_info["name"],
                           image_url=id_info["picture"], email=email_verify, locale=id_info["locale"])
            db.session.add(db_user)
            db.session.commit()
    return db_user


@app.route("/api/login", methods=["POST"])
def login():
    try:
        db_user = load_user_from_request(request)
        login_user(db_user)
        resp = make_response(json.dumps(db_user.to_json()))
        return resp
    except:
        abort(403)


@app.route("/api/demologin", methods=["GET"])
def demologin():
    db_user = User.query.filter_by(id=0).one()
    login_user(db_user)
    resp = make_response(json.dumps(db_user.to_json()))
    return resp


@app.route("/api/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    resp = make_response(json.dumps({"success": True}))
    return resp



