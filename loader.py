from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
from app import Item
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


def loader():
    top_id_obj = Item.query.order_by(Item.id.desc()).first()
    base_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    obj_ids = requests.get(base_url).json()['objectIDs']
    index = obj_ids.index(top_id_obj.id)
    obj_ids = obj_ids[index + 1:]
    print(len(obj_ids))
    counter = 0
    save_total = 0
    errors = []
    for obj_id in obj_ids:
        counter += 1
        response = requests.get(base_url + "/{}".format(obj_id)).json()
        new_item_dict = {
            "api_id": response.get("objectID"),
            "repository": response.get("repository"),
            "highlight": response.get("isHighlight", False),
            "public_domain": response.get("isPublicDomain", True),
            "primary_image": response.get("primaryImage"),
            "title": response.get("title"),
            "department": response.get("department"),
            "artist": response.get("artistDisplayName"),
            "artist_bio": response.get("artistDisplayBio"),
            "obj_date": response.get("objectDate"),
            "obj_begin_date": response.get("objectBeginDate"),
            "obj_end_date": response.get("objectEndDate"),
            "medium": response.get("medium"),
            "dimensions": response.get("dimensions")
        }
        if new_item_dict['primary_image'].startswith("http"):
            new_item = Item(**new_item_dict)
            try:
                print("{}, {}".format(new_item.title, new_item.artist))
                db.session.add(new_item)
                db.session.commit()
            except:
                errors.append(new_item_dict)
                db.session.rollback()
            if counter >= 100:
                save_total += counter
                print("saving, {} remaining".format(len(obj_ids) - save_total))
                db.session.commit()
                counter = 0
    db.session.commit()
    print("done")
    print errors

loader()

#   'city': 'Pittsburgh',
#   'state': 'Pennsylvania',
#   'county': '',
#   'country': 'United States',
#   'region': 'Mid-Atlantic',
#   'subregion': '',
#   'locale': '',
#   'locus': '',
#   'excavation': '',
#   'river': '',
#   'classification': 'Glass',
#   'rightsAndReproduction': '',
#   'linkResource': '',

