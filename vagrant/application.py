# Standard library imports.
import json
import random
import re
import string
from datetime import datetime
from datetime import timedelta
from unicodedata import normalize

# Third-party imports.
import httplib2
import requests
from flask import abort
from flask import flash
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask import url_for
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker

# Application-specific imports.
from catalog import Base
from catalog import Category
from catalog import Item
from catalog import ITEM_IMAGE_DIRECTORY
from catalog import User


# Define constants.
SITE_TITLE = 'Music Shop'
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Set up the app.
app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db_session = sessionmaker(bind = engine)
catalog = db_session()


# Returns a nonce value to be used as an anti-CSRF token.
def get_nonce():
    return ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))


# Returns a slug to be used as an item id.
def slugify(text):
    punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    delim = u'-'
    result = []
    for word in punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


# Aborts if user is not logged in.
def logged_in():
    return 'username' in session

# Make logged_in() available to templates as logged_in().
app.jinja_env.globals['logged_in'] = logged_in


# Generates an anti-CSRF token to be used for POST requests.
def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = get_nonce()
    print session['csrf_token']
    return session['csrf_token']

# Make generate_csrf_token() available to templates as csrf_token().
app.jinja_env.globals['csrf_token'] = generate_csrf_token


# Returns the requested Category object or aborts if it doesn't exist.
def get_category_or_abort(category_id):
    try:
        return catalog.query(Category).filter_by(id = category_id).one()
    except:
        abort(404)


# Helper that concatenates the XML output from a list of items into proper XML.
def xmlify(items):
    lines = []
    lines.append('<?xml version="1.0"?>')
    lines.append('<items>')
    lines += [i.xml for i in items]
    lines.append('</items>')
    return '\n'.join(lines)


# Returns the requested Item object or aborts if it doesn't exist. Or if the
# item exists in the database, but it isn't linked to the specified category,
# then abort() will be called.
def get_item_or_abort(item_id, category_id):
    try:
        return catalog.query(Item).filter_by(id = item_id, category_id = category_id).one()
    except:
        abort(404)


# Helper method that clears the user session context.
def reset_session():
    del session['credentials']
    del session['gplus_id']
    del session['username']
    del session['email']
    del session['picture']
    del session['csrf_token']
    del session['user_id']


def get_user_id(email):
    try:
        user = catalog.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def get_user_info(user_id):
    user = catalog.query(User).filter_by(id = user_id).one()
    return user


def update_user_info(user_id, name, picture):
    user = catalog.query(User).filter_by(id = user_id).one()
    user.name = name
    user.picture = picture
    catalog.add(user)
    catalog.commit()


def create_user(name, email, picture):
    user = User(name = name,
                email = email,
                picture = picture,
                admin = False)
    catalog.add(user)
    catalog.commit()
    user = catalog.query(User).filter_by(email = session['email']).one()
    return user.id


def admin():
    return 'user_id' in session and get_user_info(session['user_id']).admin

# Make admin() available to templates as admin().
app.jinja_env.globals['admin'] = admin


def allowed_to_change_item(item):
    return (
        'user_id' in session
        and (item.user_id == session['user_id'] or admin())
    )


# Filter for creating the proper title for the templates.
@app.template_filter('title')
def title_filter(page_title):
    if not page_title:
        return SITE_TITLE
    else:
        return "%s | %s" % (page_title, SITE_TITLE)


# Context Processor that makes category list available in templates.
@app.context_processor
def inject_categories():
    categories = catalog.query(Category).all()
    return dict(categories = categories)


# Verifies that all POST requests have the correct anti-CSRF token.
@app.before_request
def csrf_protect():
    if request.method == 'POST':
        post_token = request.form.get('_csrf_token')
        session_token = session.get('csrf_token')
        if post_token is None or post_token != session_token:
            flash("Session expired")
            return redirect(url_for('show_main'))


@app.route('/img/<filename>')
def serve_image(filename):
    return send_from_directory(ITEM_IMAGE_DIRECTORY, filename)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    code = request.form.get('code')
    try:
        # Upgrade the authorization code into a credentials object.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = '')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID doesn't match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in.
    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['credentials'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    # If the name field isn't blank, set the user's name to that. Otherwise,
    # set the user's name to their email address.
    if data['name']:
        session['username'] = data['name']
    else:
        session['username'] = data['email']
    session['email'] = data['email']
    session['picture'] = data['picture']

    # Check if user exists in database and update their info just in case any
    # of their info has changed since their last login. If the user doesn't
    # exist, create new user.
    user_id = get_user_id(session['email'])
    if not user_id:
        user_id = create_user(session['username'], session['email'],
                              session['picture'])
    else:
        update_user_info(user_id, session['username'], session['picture'])
    session['user_id'] = user_id

    # Inform user that they are logged in.
    flash("You have signed in as %s" % session['username'])
    return "Login successful."


@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    # Only disconnect a connected user.
    credentials = session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        reset_session()
        flash("You have signed out")
        return "Logout successul."
    else:
        # For whatever reason, the given token was invalid.
        reset_session()
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
def show_main():
    items = catalog.query(Item).order_by(desc(Item.created)).limit(10).all()
    return render_template('show_main.html', items = items)


@app.route('/<category_id>/')
def show_items(category_id):
    category = get_category_or_abort(category_id)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return render_template('show_items.html', category = category,
                           items = items)


@app.route('/my-items/')
def show_user_items():
    if not logged_in():
        return redirect(url_for('show_main'))
    items = (
        catalog.query(Item)
            .filter_by(user_id = session['user_id'])
            .order_by(Item.name)
            .all()
    )
    return render_template('my_items.html', items = items)


@app.route('/<category_id>/<item_id>')
def show_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return render_template('show_item.html', item = item,
                           user_authorized = allowed_to_change_item(item))


@app.route('/<category_id>/new', methods = ['GET', 'POST'])
def new_item(category_id):
    if not logged_in():
        return redirect(url_for('show_items', category_id = category_id))
    category = get_category_or_abort(category_id)
    if request.method == 'POST':
        item_name = request.form['name']
        item_id = slugify(item_name)
        item_desc = request.form['description']
        item_short_desc = request.form['short_description']
        item_price = request.form['price']
        item = Item(id = item_id, name = item_name, description = item_desc,
                    short_description = item_short_desc,
                    price = item_price, category_id = category.id,
                    user_id = session['user_id'])
        item.save_image(request.files['image_file'])
        catalog.add(item)
        catalog.commit()
        flash("Item created: %s" % item.name)
        return redirect(url_for('show_item', category_id = category.id,
                                item_id = item_id))
    else:
        return render_template('new_item.html', category = category)


@app.route('/<category_id>/<item_id>/edit', methods = ['GET', 'POST'])
def edit_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    if not allowed_to_change_item(item):
        return redirect(url_for('show_item', category_id = category_id,
                                item_id = item_id))
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.short_description = request.form['short_description']
        item.price = request.form['price']
        item.category_id = request.form['category_id']
        item.save_image(request.files['image_file'])
        catalog.add(item)
        catalog.commit()
        flash("Item saved: %s" % item.name)
        return redirect(url_for('show_item', category_id = item.category_id,
                                item_id = item.id))
    else:
        return render_template('edit_item.html', item = item)


@app.route('/<category_id>/<item_id>/delete', methods = ['GET', 'POST'])
def delete_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    if not allowed_to_change_item(item):
        return redirect(url_for('show_item', category_id = category_id,
                                item_id = item_id))
    if request.method == 'POST':
        item.delete_image()
        catalog.delete(item)
        catalog.commit()
        flash("Item deleted: %s" % item.name)
        return redirect(url_for('show_items', category_id = item.category_id))
    else:
        return render_template('delete_item.html', item = item)


@app.route('/user-management/', methods = ['GET', 'POST'])
def user_management():
    if not admin():
        return redirect(url_for('show_main'))
    users = (
        catalog.query(User)
            .filter(User.id != session['user_id'])
            .order_by(User.email)
            .all()
    )
    if request.method == 'POST':
        for user in users:
            if user.email in request.form:
                user.admin = request.form[user.email] == 'admin'
                catalog.add(user)
        catalog.commit()
        flash("User settings have been saved")
        return redirect(url_for('user_management'))
    else:
        return render_template('user_management.html', users = users)


# JSON endpoints.
@app.route('/catalog.json')
def show_all_items_json():
    items = catalog.query(Item).order_by(Item.category_id).order_by(Item.name).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/<category_id>.json')
def show_items_json(category_id):
    category = get_category_or_abort(category_id)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/<category_id>/<item_id>.json')
def show_item_json(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return jsonify(Item=item.serialize)


# XML endpoints.
@app.route('/catalog.xml')
def show_all_items_xml():
    items = catalog.query(Item).order_by(Item.category_id).order_by(Item.name).all()
    return xmlify(items)


@app.route('/<category_id>.xml')
def show_items_xml(category_id):
    category = get_category_or_abort(category_id)
    items = catalog.query(Item).filter_by(category_id = category.id).order_by(Item.name).all()
    return xmlify(items)


@app.route('/<category_id>/<item_id>.xml')
def show_item_xml(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return xmlify([item])


# Run the application.
if __name__ == '__main__':
    app.secret_key = 'horrible_secret_key_man'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
