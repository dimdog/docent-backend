from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from date_parser import rijks_date_parser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db = SQLAlchemy(app)
from model import Item

for item in db.session.query(Item).filter_by(repository_id=2):
    before_date, after_date = rijks_date_parser(item.obj_date)
    item.obj_begin_date = before_date
    item.obj_end_date = after_date

db.session.commit()
