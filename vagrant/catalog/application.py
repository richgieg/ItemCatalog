from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db_session = sessionmaker(bind = engine)
catalog = db_session()


# Define constant for the site's primary title.
SITE_TITLE = "Music Shop"


# Filter for creating the proper title for the templates.
@app.template_filter('title')
def title_filter(page_title):
    if not page_title:
        return SITE_TITLE
    else:
        return "%s | %s" % (page_title, SITE_TITLE)


# Helper for creating item_id from an item's name.
def make_item_id(name):
    return name.replace("'", '').replace('"', '').replace(' ', '-').lower()


# Helper that makes category list available in templates.
@app.context_processor
def inject_categories():
    categories = catalog.query(Category).all()
    return dict(categories = categories)


@app.route('/login')
def login():
    session['username'] = 'dummy'
    return redirect(url_for('show_main'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('show_main'))


@app.route('/')
def show_main():
    items = catalog.query(Item).order_by(desc(Item.created)).limit(10).all()
    return render_template('show_main.html', items = items)


@app.route('/<string:category_id>/')
def show_items(category_id):
    try:
        category = catalog.query(Category).filter_by(id = category_id).one()
    except:
        abort(404)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return render_template('show_items.html', category = category,
                           items = items)


@app.route('/<string:category_id>/<string:item_id>')
def show_item(category_id, item_id):
    try:
        category = catalog.query(Category).filter_by(id = category_id).one()
        item = catalog.query(Item).filter_by(id = item_id).one()
    except:
        abort(404)
    return render_template('show_item.html', item = item)


@app.route('/<string:category_id>/new', methods = ['GET', 'POST'])
def new_item(category_id):
    if 'username' not in session:
        abort(404)
    try:
        category = catalog.query(Category).filter_by(id = category_id).one()
    except:
        abort(404)
    if request.method == 'POST':
        item_name = request.form['name']
        item_id = make_item_id(item_name)
        item_desc = request.form['description']
        item_price = request.form['price']
        item = Item(id = item_id, name = item_name, description = item_desc,
                    price = item_price, category_id = category.id)
        catalog.add(item)
        catalog.commit()
        flash("Item created")
        return redirect(url_for('show_item', category_id = category.id,
                                item_id = item_id))
    else:
        return render_template('new_item.html', category = category)


@app.route('/<string:category_id>/<string:item_id>/edit', methods = ['GET', 'POST'])
def edit_item(category_id, item_id):
    if 'username' not in session:
        abort(404)
    try:
        category = catalog.query(Category).filter_by(id = category_id).one()
        item = catalog.query(Item).filter_by(id = item_id).one()
    except:
        abort(404)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        item.category_id = request.form['category_id']
        catalog.add(item)
        catalog.commit()
        flash("Item updated")
        return redirect(url_for('show_item', category_id = item.category_id,
                                item_id = item.id))
    else:
        return render_template('edit_item.html', item = item)


@app.route('/<string:category_id>/<string:item_id>/delete', methods = ['GET', 'POST'])
def delete_item(category_id, item_id):
    if 'username' not in session:
        abort(404)
    try:
        category = catalog.query(Category).filter_by(id = category_id).one()
        item = catalog.query(Item).filter_by(id = item_id).one()
    except:
        abort(404)
    if request.method == 'POST':
        catalog.delete(item)
        catalog.commit()
        flash("Item '%s' deleted" % item.name)
        return redirect(url_for('show_items', category_id = item.category_id))
    else:
        return render_template('delete_item.html', item = item)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
