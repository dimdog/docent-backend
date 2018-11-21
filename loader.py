import requests
from model import Item
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(os.environ['DATABASE_URL'])
session = sessionmaker(bind=engine)


def loader():
    top_id_obj = session.query(Item).order_by(Item.id.desc()).first()
    base_url = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
    obj_ids = requests.get(base_url).json()['objectIDs']
    if top_id_obj:
        index = obj_ids.index(top_id_obj.id)
        obj_ids = obj_ids[index + 1:]
    print(len(obj_ids))
    counter = 0
    save_total = 0
    errors = []
    for obj_id in obj_ids:
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
            "dimensions": response.get("dimensions"),
            "city": response.get("city"),
            "state": response.get("state"),
            "county": response.get("county"),
            "country": response.get("country"),
            "region": response.get("region"),
            "subregion": response.get("subregion"),
            "locale": response.get("locale"),
            "portfolio": response.get("portfolio"),
            "creditLine": response.get("creditLine")
        }
        if new_item_dict['primary_image'].startswith("http") and new_item_dict['highlight']:
            counter += 1
            new_item = Item(**new_item_dict)
            try:
                print("{}, {}".format(new_item.title, new_item.artist))
                session.add(new_item)
                session.commit()
            except:
                errors.append(new_item_dict)
                session.rollback()
            if counter == 100:
                save_total += counter
                print("saving, {} remaining".format(len(obj_ids) - save_total))
                session.commit()
                counter = 0
                if save_total == 6000:
                    break
    session.commit()
    print("done")
    print(errors)

loader()
