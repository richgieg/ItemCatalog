import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from xml.etree import ElementTree as ET

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
    image_path = Column(String(80))
    created = Column(DateTime, default=func.now())
    category_id = Column(String(80), ForeignKey('categories.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_path': self.image_path,
            'category_id': self.category_id
        }

    @property
    def xml(self):
        item = ET.Element('item')
        category_id = ET.SubElement(item, 'category_id')
        category_id.text = self.category_id
        description = ET.SubElement(item, 'description')
        description.text = self.description
        item_id = ET.SubElement(item, 'id')
        item_id.text = self.id
        image_path = ET.SubElement(item, 'image_path')
        image_path.text = self.image_path
        name = ET.SubElement(item, 'name')
        name.text = self.name
        price = ET.SubElement(item, 'price')
        price.text = self.price
        return ET.tostring(item)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
