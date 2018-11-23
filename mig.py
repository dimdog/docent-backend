from model import Item, Artist, Repository, Department
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

first_item = Item.query.first()
print first_item
rep_dict = {"name": first_item.repository,
            "city": "New York",
            "state": "NY",
            "country": "United States of America"}
rep = Repository(**rep_dict)
session.add(rep)
session.commit()
