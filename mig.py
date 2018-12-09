from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import imageio
import urllib.request



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)
from model import Item

fname="temp.{}"

for item in db.session.query(Item)[:1]:
    if item.primary_image and not (item.primary_image_height or item.primary_image_width):
        print(item.primary_image)
        file_name = fname.format(item.primary_image.split(".")[-1])
        urllib.request.urlretrieve(item.primary_image, file_name)
        im = imageio.imread(file_name)
        print(dir(im))
        print(im)
        print(im.shape)
        print(im.meta)


# db.session.commit()
