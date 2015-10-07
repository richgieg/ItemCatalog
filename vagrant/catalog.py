import os
from datetime import datetime
from xml.etree import ElementTree as ET
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


# Define constants.
ITEM_IMAGE_DIRECTORY = 'img'
ALLOWED_IMAGE_EXTENSIONS = set(['jpg', 'png'])
DEFAULT_IMAGE = '/static/default.png'


# Define ORM base class.
Base = declarative_base()


# Helper that checks if image file is of a legal file type.
def allowed_image_file(filename):
    return ('.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    picture = Column(String(256), nullable=False)
    group = Column(String(10), nullable=False)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(String(256), primary_key=True)
    name = Column(String(256), nullable=False)


class Item(Base):
    __tablename__ = 'items'
    id = Column(String(256), primary_key=True)
    name = Column(String(256), nullable=False)
    short_description = Column(String(256))
    description = Column(String(1024))
    price = Column(String(10))
    image_path = Column(String(256))
    created = Column(DateTime, default=func.now())
    category_id = Column(String(256), ForeignKey('categories.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    # Save uploaded image to disk and set item's image_path field. If file is
    # blank, and this is a brand new item, then set the item's image_path field
    # to DEFAULT_IMAGE.
    def save_image(self, file):
        if file and allowed_image_file(file.filename):
            self.delete_image()
            filename, extension = os.path.splitext(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = '%s-%s%s' % (self.id, timestamp, extension.lower())
            image_path = os.path.join(ITEM_IMAGE_DIRECTORY, filename)
            file.save(image_path)
            # Add leading slash so path works in HTML img tags.
            self.image_path = '/' + image_path
        else:
            if self.image_path is None:
                self.image_path = DEFAULT_IMAGE

    # Delete image file from disk, if exists.
    def delete_image(self):
        if self.image_path and self.image_path != DEFAULT_IMAGE:
            # Skip the initial slash in file path.
            os.remove(self.image_path[1:])

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
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
        short_description = ET.SubElement(item, 'short_description')
        short_description.text = self.short_description
        item_id = ET.SubElement(item, 'id')
        item_id.text = self.id
        image_path = ET.SubElement(item, 'image_path')
        image_path.text = self.image_path
        name = ET.SubElement(item, 'name')
        name.text = self.name
        price = ET.SubElement(item, 'price')
        price.text = self.price
        return ET.tostring(item)
