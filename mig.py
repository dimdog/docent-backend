from model import Item, Artist, Repository, Department
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine(os.environ['DATABASE_URL'])
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


first_item = session.query(Item).first()
rep_dict = { "name": first_item.repository,
             "city": "New York",
             "state": "NY",
             "country": "United States of America"}
rep = Repository(**rep_dict)
session.add(rep)
session.commit()
