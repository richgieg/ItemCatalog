import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'
    id = Column(String(80), primary_key=True)
    name = Column(String(80), nullable=False)


class Item(Base):
    __tablename__ = 'items'
    id = Column(String(80), primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(1000))
    price = Column(String(10))
    created = Column(DateTime, default=func.now())
    category_id = Column(String(80), ForeignKey('categories.id'))
    category = relationship(Category)

    def serialize(self, include_category=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price
        }
        if include_category:
            data['category_id'] = self.category_id
        return data


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
