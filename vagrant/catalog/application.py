from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
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


# Aborts if user is not logged in.
def abort_if_not_logged_in():
    if 'username' not in session:
        abort(404)


# Returns the requested Category object or aborts if it doesn't exist.
def get_category_or_abort(category_id):
    try:
        return catalog.query(Category).filter_by(id = category_id).one()
    except:
        abort(404)


# Returns the requested Item object or aborts if it doesn't exist. Or if the
# item exists in the database, but it isn't linked to the specified category,
# then abort() will be called.
def get_item_or_abort(item_id, category_id):
    try:
        return catalog.query(Item).filter_by(id = item_id, category_id = category_id).one()
    except:
        abort(404)


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


# Helper that concatenates the XML output from a list of items into proper XML.
def xmlify(items):
    lines = []
    lines.append('<?xml version="1.0"?>')
    lines.append('<items>')
    lines += [i.xml for i in items]
    lines.append('</items>')
    return '\n'.join(lines)


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
    category = get_category_or_abort(category_id)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return render_template('show_items.html', category = category,
                           items = items)


@app.route('/<string:category_id>/<string:item_id>')
def show_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return render_template('show_item.html', item = item)


@app.route('/<string:category_id>/new', methods = ['GET', 'POST'])
def new_item(category_id):
    abort_if_not_logged_in()
    category = get_category_or_abort(category_id)
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
    abort_if_not_logged_in()
    item = get_item_or_abort(item_id, category_id)
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
    abort_if_not_logged_in()
    item = get_item_or_abort(item_id, category_id)
    if request.method == 'POST':
        catalog.delete(item)
        catalog.commit()
        flash("Item '%s' deleted" % item.name)
        return redirect(url_for('show_items', category_id = item.category_id))
    else:
        return render_template('delete_item.html', item = item)


# JSON / XML endpoints
@app.route('/catalog.json')
def show_all_items_json():
    items = catalog.query(Item).order_by(Item.category_id).order_by(Item.name).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog.xml')
def show_all_items_xml():
    items = catalog.query(Item).order_by(Item.category_id).order_by(Item.name).all()
    return xmlify(items)


@app.route('/<string:category_id>.json')
def show_items_json(category_id):
    category = get_category_or_abort(category_id)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/<string:category_id>.xml')
def show_items_xml(category_id):
    category = get_category_or_abort(category_id)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return xmlify(items)


@app.route('/<string:category_id>/<string:item_id>.json')
def show_item_json(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return jsonify(Item=item.serialize)


@app.route('/<string:category_id>/<string:item_id>.xml')
def show_item_xml(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return xmlify([item])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
