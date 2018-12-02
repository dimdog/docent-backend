import requests
from model import Item, Repository, Artist, ItemLanguage, Department
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

apikey = os.environ["RIJKS_KEY"]


def search():
    for x in range(1, 10):
        res = requests.get("https://www.rijksmuseum.nl/api/en/collection?key={}&format=json&p={}&ps=100&imgonly=True&st=Objects".format(apikey, x)).json()
        for obj in res['artObjects']:
            obj_id = obj['objectNumber']
            item = session.query(Item).filter_by(api_id=obj_id).first()
            if not item:
                loader(obj_id)


def loader(obj_id):
    base_url = "https://www.rijksmuseum.nl/api/{}/collection/{}?key={}&format=json".format("en", obj_id, apikey)
    response = requests.get(base_url).json()
    nl_url = "https://www.rijksmuseum.nl/api/{}/collection/{}?key={}&format=json".format("nl", obj_id, apikey)
    nl_response = requests.get(nl_url).json()
    artObject = response["artObject"]
    artObjectPage = response["artObjectPage"]
    nl_artObject = nl_response["artObject"]
    nl_artObjectPage = nl_response["artObjectPage"]
    repository = session.query(Repository).filter_by(name="Rijksmuseum").first()
    department = None
    if artObject["objectCollection"]:
        department = session.query(Department).filter_by(repository_id=repository.id, name=artObject["objectCollection"][0]).first()
        if department is None:
            new_department = Department(repository_id=repository.id, name=artObject["objectCollection"][0])
            session.add(new_department)
            session.commit()
    artist_name = artObject["principalOrFirstMaker"]
    artist = None
    if artist_name and artist_name is not "anonymous":
        artist = session.query(Artist).filter_by(name=artist_name).first()
        if not artist:
            for pm in artObject["principalMakers"]:
                if pm["name"] == artist_name:
                    birth_date = pm["dateOfBirth"]
                    death_date = pm["dateOfDeath"]
                    artist = Artist(name=artist_name, birth_date=birth_date, death_date=death_date, bio=pm["biography"])
                    session.add(artist)
                    session.commit()
            if artist is None:
                return
    else:
        artist = session.query(Artist).filter_by(name="Unknown").one()
    webImage = artObject.get("webImage", {})
    primary_image = None
    if webImage and "url" in webImage:
        primary_image = webImage["url"]
    else:
        return
    new_item_dict = {
        "api_id": obj_id,
        "repository_id": repository.id,
        "public_domain": artObject.get("isPublicDomain", True),
        "primary_image": primary_image,
        "primary_image_height": artObject.get("webImage", {}).get("height"),
        "primary_image_width": artObject.get("webImage", {}).get("width"),
        "artist_id": artist.id,
        "obj_date": artObject.get("dating", {}).get("presentingDate"),
    }
    if department:
        new_item_dict["department_id"] = department.id
    new_item = Item(**new_item_dict)
    session.add(new_item)
    session.commit()
    en_language_dict = {
        "item_id": new_item.id,
        "language": "EN",
        "title": artObject.get("title"),
        "description": artObjectPage.get("plaqueDescription"),
        "creditLine": artObject.get("acquisition", {}).get("creditLine"),
        "medium": artObject.get("physicalMedium"),
        "audiofile": artObjectPage.get("audioFile1")
    }
    nl_language_dict = {
        "item_id": new_item.id,
        "language": "NL",
        "title": nl_artObject.get("title"),
        "description": nl_artObject.get("description"),
        "creditLine": nl_artObject.get("acquisition", {}).get("creditLine"),
        "medium": nl_artObject.get("physicalMedium"),
        "audiofile": nl_artObjectPage.get("audioFile1")
    }
    en_il = ItemLanguage(**en_language_dict)
    nl_il = ItemLanguage(**nl_language_dict)
    session.add(en_il)
    session.add(nl_il)
    session.commit()
    print(en_il.title)

search()
