from flask import Flask, render_template, request
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)
engine = create_engine('sqlite:///shop_menu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


# Helper for building navigation in layout.html.
@app.context_processor
def inject_categories():
    categories = session.query(Category).all()
    return dict(categories = categories)


@app.route('/')
def show_main():
    items = session.query(Item).order_by(desc(Item.created)).limit(10).all()
    return render_template('show_main.html', items = items)


@app.route('/<string:category_id>/')
def show_items(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    items = session.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return render_template('show_items.html', category_name = category.name,
                           items = items)


@app.route('/<string:category_id>/<string:item_id>')
def show_item(category_id, item_id):
    return render_template('show_item.html', category_id = category_id,
                           item_id = item_id)


@app.route('/items/new', methods = ['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        pass
    else:
        return render_template('new_item.html')


@app.route('/items/<string:item_id>/edit', methods = ['GET', 'POST'])
def edit_item(item_id):
    if request.method == 'POST':
        pass
    else:
        return render_template('edit_item.html', item_id = item_id)


@app.route('/items/<string:item_id>/delete', methods = ['GET', 'POST'])
def delete_item(item_id):
    if request.method == 'POST':
        pass
    else:
        return render_template('delete_item.html', item_id = item_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)