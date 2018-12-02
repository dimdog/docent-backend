from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)
from model import Item, ItemLanguage


for item in db.session.query(Item):
    il = ItemLanguage(item_id=item.id, language="EN", title=item.title, medium=item.medium, dimensions=item.dimensions,
                      creditLine=item.creditLine)
    db.session.add(il)

db.session.commit()
