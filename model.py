from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


app = Flask(__name__)
db = SQLAlchemy(app)


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


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1028))
    bio = db.Column(db.String(1028))
    birth_date = db.Column(db.String(1028))  # will make this better later
    death_date = db.Column(db.String(1028))  # will make this better later
    # TODO make birth and death locations?


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, nullable=False)
    repository_id = db.Column(db.String(1028), db.ForeignKey("repository.id"), nullable=False)
    department_id = db.Column(db.String(1028), db.ForeignKey("department.id"))
    artist_id = db.Column(db.String(1028), db.ForeignKey("artist.id"))
    highlight = db.Column(db.Boolean, nullable=False)
    public_domain = db.Column(db.Boolean, nullable=False)
    primary_image = db.Column(db.String(1028), nullable=False)
    # TODO handle "additionalImages"
    title = db.Column(db.String(1028), nullable=False)
    obj_date = db.Column(db.String(1028))  # make this into a DATE! Maybe a great thing to test a tensor flow parser on! #machinelearning #$$$$
    obj_begin_date = db.Column(db.String(1028))
    obj_end_date = db.Column(db.String(1028))
    medium = db.Column(db.String(1028), nullable=False)
    dimensions = db.Column(db.String(1028), nullable=False)
    city = db.Column(db.String(1028))
    state = db.Column(db.String(1028))
    county = db.Column(db.String(1028))
    country = db.Column(db.String(1028))
    region = db.Column(db.String(1028))
    subregion = db.Column(db.String(1028))
    locale = db.Column(db.String(1028))
    portfolio = db.Column(db.String(1028))
    creditLine = db.Column(db.String(1028))
    description_en = db.Column(db.String(1028))
    description_nl = db.Column(db.String(1028))
    description_es = db.Column(db.String(1028))
    description_fr = db.Column(db.String(1028))
    description_gr = db.Column(db.String(1028))
    repository = relationship("Repository", back_populates="items")
    department = relationship("Department", back_populates="items")
    artist = relationship("Artist", back_populates="items")

    def __repr__(self):
        return '<Item {},{}>'.format(self.title, self.id)

    def tiny(self):
        return {'id': self.id, 'title': self.title, 'primary_image': self.primary_image}

    def full(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        d["artist"] = self.artist.name
        d["repository"] = self.repository.name
        d["deparmtnet"] = self.department.name
        return d

