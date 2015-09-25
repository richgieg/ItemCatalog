from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog import Base, Category

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db_session = sessionmaker(bind = engine)
catalog = db_session()

categories = [
    {
        'id': 'guitars',
        'name': 'Guitars'
    },
    {
        'id': 'bass',
        'name': 'Bass Guitars'
    },
    {
        'id': 'amplifiers-effects',
        'name': 'Amplifiers & Effects'
    },
    {
        'id': 'drums-percussion',
        'name': 'Drums & Percussion'
    },
    {
        'id': 'live-sound',
        'name': 'Live Sound'
    },
    {
        'id': 'recording-gear',
        'name': 'Recording'
    },
    {
        'id': 'accessories',
        'name': 'Accessories'
    }
]

for category in categories:
    catalog.add(Category(id = category['id'], name = category['name']))

catalog.commit()
