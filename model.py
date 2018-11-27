from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import func

import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    family_name = db.Column(db.String(100))
    given_name = db.Column(db.String(100))
    full_name = db.Column(db.String(100))
    image_url = db.Column(db.String(1028))
    email = db.Column(db.String(100), nullable=False, unique=True)
    locale = db.Column(db.String(100))  # language preference
    likes = relationship("UserLikes")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return "{}".format(self.id)

    def to_json(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


class UserLikes(db.Model):
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    date_updated = db.Column(db.DateTime, nullable=False, server_default=func.now())
    item = relationship("Item", backref="userlikes")


class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1028))
    city = db.Column(db.String(1028))
    state = db.Column(db.String(1028))
    country = db.Column(db.String(1028))


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1028))
    repository_id = db.Column(db.Integer, db.ForeignKey("repository.id"), nullable=False)
    repository = relationship("Repository", backref="departments")


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1028))
    bio = db.Column(db.String(1028))  # will need multilingual support TODO
    birth_date = db.Column(db.String(1028))  # will make this better later
    death_date = db.Column(db.String(1028))  # will make this better later
    # TODO make birth and death locations?


class ItemLanguage(db.Model):
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False, primary_key=True)
    language = db.Column(db.String(10), nullable=False, primary_key=True)
    title = db.Column(db.TEXT, nullable=False)
    medium = db.Column(db.TEXT)
    dimensions = db.Column(db.TEXT)
    creditLine = db.Column(db.TEXT)
    description = db.Column(db.TEXT)
    audiofile = db.Column(db.String(1028))

    def to_dict(self):
        return {"language": self.language, "title": self.title, "medium": self.medium, "dimensions": self.dimensions, "creditLine": self.creditLine,
                "description": self.description, "audiofile": self.audiofile}


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.String(1028), nullable=False)
    repository_id = db.Column(db.String(1028), db.ForeignKey("repository.id"), nullable=False)
    department_id = db.Column(db.String(1028), db.ForeignKey("department.id"))
    artist_id = db.Column(db.String(1028), db.ForeignKey("artist.id"))
    public_domain = db.Column(db.Boolean, nullable=False)
    primary_image = db.Column(db.String(1028), nullable=False)
    # TODO handle "additionalImages"
    obj_date = db.Column(db.String(1028))  # make this into a DATE! Maybe a great thing to test a tensor flow parser on! #machinelearning #$$$$
    obj_begin_date = db.Column(db.String(1028))
    obj_end_date = db.Column(db.String(1028))
    city = db.Column(db.String(1028))
    state = db.Column(db.String(1028))
    county = db.Column(db.String(1028))
    country = db.Column(db.String(1028))
    region = db.Column(db.String(1028))
    subregion = db.Column(db.String(1028))
    locale = db.Column(db.String(1028))
    portfolio = db.Column(db.String(1028))
    primary_image_height = db.Column(db.Integer)
    primary_image_width = db.Column(db.Integer)
    repository = relationship("Repository", backref="items")
    department = relationship("Department", backref="items")
    artist = relationship("Artist", backref="items")
    languages = relationship("ItemLanguage", collection_class=attribute_mapped_collection('language'), backref="item")

    def __repr__(self):
        return '<Item {},{}>'.format(self.title, self.id)

    def tiny(self):
        return {'id': self.id, 'title': self.languages["EN"].title, 'primary_image': self.primary_image}

    def full(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        d["artist"] = self.artist.name
        d["repository"] = self.repository.name
        if self.department:
            d["department"] = self.department.name
        languages = {}
        for lang, obj in self.languages.items():
            languages[lang] = obj.to_dict()
        d["languages"] = languages
        return d

db.create_all()
