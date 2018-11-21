from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_id = Column(Integer, nullable=False)
    repository = Column(String(1028), nullable=False)  # no shit make this its own object TODO
    highlight = Column(Boolean, nullable=False)
    public_domain = Column(Boolean, nullable=False)
    primary_image = Column(String(1028), nullable=False)
    #  TODO handle "additionalImages"
    title = Column(String(1028), nullable=False)
    department = Column(String(1028), nullable=False)  # make this an id / reference?
    artist = Column(String(1028), nullable=False)  # definitely make an artist table
    artist_bio = Column(String(1028))  # duhhhhhhhh
    obj_date = Column(String(1028))  # make this into a DATE! Maybe a great thing to test a tensor flow parser on! #machinelearning #$$$$
    obj_begin_date = Column(String(1028))
    obj_end_date = Column(String(1028))
    medium = Column(String(1028), nullable=False)
    dimensions = Column(String(1028), nullable=False)
    city = Column(String(1028))
    state = Column(String(1028))
    county = Column(String(1028))
    country = Column(String(1028))
    region = Column(String(1028))
    subregion = Column(String(1028))
    locale = Column(String(1028))
    portfolio = Column(String(1028))
    creditLine = Column(String(1028))

    def __repr__(self):
        return '<Item {},{}>'.format(self.title, self.id)

    def tiny(self):
        return {'id': self.id, 'title': self.title, 'primary_image': self.primary_image}

    def full(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = str(getattr(self, column.name))
        return d

