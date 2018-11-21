from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

import simplejson as json

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wake@localhost/docent'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_id = db.Column(db.Integer, nullable=False)
    repository = db.Column(db.String(1028), nullable=False)  # no shit make this its own object TODO
    highlight = db.Column(db.Boolean, nullable=False)
    public_domain = db.Column(db.Boolean, nullable=False)
    primary_image = db.Column(db.String(1028), nullable=False)
    #  TODO handle "additionalImages"
    title = db.Column(db.String(1028), nullable=False)
    department = db.Column(db.String(1028), nullable=False)  # make this an id / reference?
    artist = db.Column(db.String(1028), nullable=False)  # definitely make an artist table
    artist_bio = db.Column(db.String(1028))  # duhhhhhhhh
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

    def __repr__(self):
        return '<Item {},{}>'.format(self.title, self.id)

    def tiny(self):
        return {'id': self.id, 'title': self.title, 'primary_image': self.primary_image}

    def full(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d


@app.route("/")
def index():
    return json.dumps({"items": [item.tiny() for item in Item.query.all()]})


@app.route("/<int:item_id>")
def get_item(item_id):
    return json.dumps(Item.query.filter(Item.id == item_id).one().full())

print("HEREEEE")
app.run(port=int(os.environ['PORT']))
