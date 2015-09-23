from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)
engine = create_engine('sqlite:///shop_menu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


# Helper for creating item_id from an item's name.
def make_item_id(name):
    return name.replace("'", '').replace(' ', '-').lower()


# Helper for redirecting to the home page.
def go_home():
    return redirect(url_for('show_main'))


# Helper that makes category list available in templates.
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
    try:
        category = session.query(Category).filter_by(id = category_id).one()
    except:
        return go_home()
    items = session.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return render_template('show_items.html', category_name = category.name,
                           items = items)


@app.route('/<string:category_id>/<string:item_id>')
def show_item(category_id, item_id):
    try:
        category = session.query(Category).filter_by(id = category_id).one()
        item = session.query(Item).filter_by(id = item_id).one()
    except:
        return go_home()
    return render_template('show_item.html', item = item)


@app.route('/items/new', methods = ['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        item_name = request.form['name']
        item_id = make_item_id(item_name)
        item_desc = request.form['description']
        item_price = request.form['price']
        category_id = request.form['category_id']
        item = Item(id = item_id, name = item_name, description = item_desc,
                    price = item_price, category_id = category_id)
        session.add(item)
        session.commit()
    else:
        return render_template('new_item.html')


@app.route('/items/<string:item_id>/edit', methods = ['GET', 'POST'])
def edit_item(item_id):
    try:
        item = session.query(Item).filter_by(id = item_id).one()
    except:
        return go_home()
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        session.add(item)
        session.commit()
        return redirect(url_for('show_item', category_id = item.category_id,
                                item_id = item.id))
    else:
        return render_template('edit_item.html', item = item)


@app.route('/items/<string:item_id>/delete', methods = ['GET', 'POST'])
def delete_item(item_id):
    try:
        item = session.query(Item).filter_by(id = item_id).one()
    except:
        return go_home()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('show_items', category_id = item.category_id))
    else:
        return render_template('delete_item.html', item = item)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
