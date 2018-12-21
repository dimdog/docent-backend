import os
import requests
import time
from model import Item, Repository, ItemLanguage, Artist, Department

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()
start_url = "https://api.sketchfab.com/v3/search?type=models&user=calacademy"
api_key = os.environ["SKETCHFAB_API"]
headers = {'Authorization': 'Token {}'.format(api_key)}
repository = session.query(Repository).get(3)
artist = session.query(Artist).get(126)


def parse_description(description):
    split_desc = description.split("\n")
    filtered_desc = [desc.strip() for desc in split_desc if desc][:-2]
    return "\n".join(filtered_desc)


def load_chunk(url, commit=True, repeat=False, retries=0):
    try:
        response = requests.get(url, headers=headers).json()
    except:
        time.sleep(1)
        if retries == 5:
            print("Failed after 5 retries on:{}".format(url))
        retries += 1
        return load_chunk(url, commit=commit, repeat=repeat, retries=retries)
    next_url = response['next']
    print("NEXT:{}".format(next_url))
    for result_block in response['results']:
        name = result_block['name']
        api_id = result_block['uid']
        raw_description = result_block["description"]  # EN
        thumbnail = result_block['thumbnails']['images'][:3][-1]
        item_dict = {
            "api_id": api_id,
            "repository_id": repository.id,
            "artist_id": artist.id,
            "public_domain": True,
            "primary_image": thumbnail["url"],
            "primary_image_height": thumbnail["height"],
            "primary_image_width": thumbnail["width"]
        }
        if len(result_block['categories']) > 0:
            department_name = result_block['categories'][0]["name"]
            department = session.query(Department).filter_by(repository_id=repository.id, name=department_name).first()
            if department is None:
                department = Department(repository_id=repository.id, name=department_name)
                session.add(department)
                session.commit()
            item_dict["department_id"] = department.id
        new_item = Item(**item_dict)
        if commit:
            session.add(new_item)
            session.commit()
        parsed_description = parse_description(raw_description)
        en_language_dict = {
            "item_id": new_item.id,
            "language": "EN",
            "title": name,
            "description": parsed_description,
            "medium": "Bone"
        }
        en_il = ItemLanguage(**en_language_dict)
        if commit:
            session.add(en_il)
            session.commit()
    if next_url and repeat:
        time.sleep(0.3)
        load_chunk(next_url, commit=commit, repeat=repeat)

load_chunk(start_url, True, True)
