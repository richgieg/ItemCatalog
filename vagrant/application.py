#!/usr/bin/python
import json
import random
import re
import string
from datetime import datetime, timedelta
from unicodedata import normalize

import httplib2
import requests
from flask import abort, flash, Flask, jsonify, make_response, redirect, render_template, request, send_from_directory, session, url_for
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from catalog import Base, Category, Item, ITEM_IMAGE_DIRECTORY, User


# Set up the app.
app = Flask(__name__)
app.secret_key = open('secret_key', 'r').read()
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
db_session = sessionmaker(bind=engine)
catalog = db_session()


# Define constants.
SITE_TITLE = 'Music Shop'
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Make CLIENT_ID available to templates.
app.jinja_env.globals['CLIENT_ID'] = CLIENT_ID


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


# Generates an anti-CSRF token to be used for POST requests.
def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = get_nonce()
    return session['csrf_token']

# Make generate_csrf_token() available to templates as csrf_token().
app.jinja_env.globals['csrf_token'] = generate_csrf_token


# Returns the requested Category object or aborts if it doesn't exist.
def get_category_or_abort(category_id):
    try:
        return catalog.query(Category).filter_by(id=category_id).one()
    except:
        abort(404)


# Returns the requested Item object or aborts if it doesn't exist. Or if the
# item exists in the database, but it isn't linked to the specified category,
# then abort() will be called.
def get_item_or_abort(item_id, category_id):
    try:
        return (
            catalog.query(Item)
                .filter_by(id=item_id, category_id=category_id)
                .one()
        )
    except:
        abort(404)


# Concatenates the XML output from a list of items into proper XML.
def xmlify(items):
    lines = []
    lines.append('<?xml version="1.0"?>')
    lines.append('<items>')
    lines += [i.xml for i in items]
    lines.append('</items>')
    return '\n'.join(lines)


# Clears the user session context.
def reset_session():
    del session['credentials']
    del session['gplus_id']
    del session['username']
    del session['email']
    del session['picture']
    del session['csrf_token']
    del session['user_id']


# Returns the id for the user with the given email address. If the email
# address does not exist, returns None.
def get_user_id(email):
    try:
        user = catalog.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Returns a user object associated with the given id.
def get_user_info(user_id):
    user = catalog.query(User).get(user_id)
    return user


# Updates the name and picture fields of a user in the database.
def update_user_info(user_id, name, picture):
    user = catalog.query(User).get(user_id)
    user.name = name
    user.picture = picture
    catalog.add(user)
    catalog.commit()


# Creates a new user in the database.
def create_user(name, email, picture):
    user = User(name=name,
                email=email,
                picture=picture,
                group='readonly')
    catalog.add(user)
    catalog.commit()
    user = catalog.query(User).filter_by(email=email).one()
    return user.id


# Returns true if the user is signed in.
def logged_in():
    return 'username' in session

# Make logged_in() available to templates.
app.jinja_env.globals['logged_in'] = logged_in


# Returns true if the user is signed in and has standard rights or better.
def standard_rights():
    if not logged_in():
        return False
    group = get_user_info(session['user_id']).group
    return group == 'admin' or group == 'standard'

# Make standard_rights() available to templates.
app.jinja_env.globals['standard_rights'] = standard_rights


# Returns true if the user is signed in and has administrative rights.
def admin_rights():
    if not logged_in():
        return False
    group = get_user_info(session['user_id']).group
    return group == 'admin'

# Make admin_rights() available to templates.
app.jinja_env.globals['admin_rights'] = admin_rights


# Returns true if the current user is authorized to modify the given item.
def allowed_to_change_item(item):
    return (
        admin_rights() or
        (standard_rights() and item.user_id == session['user_id'])
    )


# Returns true if all required new_item form fields are not blank.
def validate_new_item_form():
    return (
        request.form['name'] and
        request.form['short_description'] and
        request.form['description'] and
        request.form['price']
    )


# Returns true if all required edit_item form fields are not blank.
def validate_edit_item_form():
    return (
        request.form['name'] and
        request.form['short_description'] and
        request.form['description'] and
        request.form['price'] and
        request.form['category_id']
    )


# Filter for creating the proper title for the templates.
@app.template_filter('title')
def title_filter(page_title):
    if not page_title:
        return SITE_TITLE
    else:
        return "%s | %s" % (page_title, SITE_TITLE)


# Context processor that makes category list available to layout template for
# purpose of building the navigation links.
@app.context_processor
def inject_categories():
    categories = catalog.query(Category).all()
    return dict(categories=categories)


# Verifies that all POST requests have the correct anti-CSRF token. If the
# _csrf_token field is not present, or does not match the current session's
# token, the browser will be redirected to the home page.
@app.before_request
def csrf_protect():
    if request.method == 'POST':
        post_token = request.form.get('_csrf_token')
        session_token = session.get('csrf_token')
        if post_token is None or post_token != session_token:
            flash("Session expired")
            return redirect(url_for('show_main'))


# Display the home page.
@app.route('/')
def show_main():
    items = catalog.query(Item).order_by(desc(Item.created)).limit(10).all()
    return render_template('show_main.html', items=items)


# Display all items in a given catagory.
@app.route('/<category_id>/')
def show_items(category_id):
    category = get_category_or_abort(category_id)
    items = (
        catalog.query(Item)
            .filter_by(category_id=category.id)
            .order_by(Item.name)
            .all()
    )
    return render_template('show_items.html', category=category,
                           items=items)


# My Items page, for signed-in users with standard rights or above.
@app.route('/my-items/')
def show_user_items():
    if not standard_rights():
        return redirect(url_for('show_main'))
    items = (
        catalog.query(Item)
            .filter_by(user_id=session['user_id'])
            .order_by(Item.name)
            .all()
    )
    return render_template('my_items.html', items=items)


# Create an item.
@app.route('/<category_id>/new', methods=['GET', 'POST'])
def new_item(category_id):
    if not standard_rights():
        return redirect(url_for('show_items', category_id=category_id))
    category = get_category_or_abort(category_id)
    if request.method == 'POST':
        if not validate_new_item_form():
            flash("Form fields cannot be blank")
            return redirect(url_for('new_item', category_id=category_id))
        item_name = request.form['name']
        item_id = slugify(item_name)
        item_desc = request.form['description']
        item_short_desc = request.form['short_description']
        item_price = request.form['price']
        item = Item(id=item_id, name=item_name, description=item_desc,
                    short_description=item_short_desc,
                    price=item_price, category_id=category.id,
                    user_id=session['user_id'])
        item.save_image(request.files['image_file'])
        catalog.add(item)
        catalog.commit()
        flash("Item created: %s" % item.name)
        return redirect(url_for('show_item', category_id=category.id,
                                item_id=item_id))
    else:
        return render_template('new_item.html', category=category)


# Read (display) an item.
@app.route('/<category_id>/<item_id>')
def show_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return render_template('show_item.html', item=item,
                           user_authorized=allowed_to_change_item(item))


# Update an item.
@app.route('/<category_id>/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    if not allowed_to_change_item(item):
        return redirect(url_for('show_item', category_id=category_id,
                                item_id=item_id))
    if request.method == 'POST':
        if not validate_edit_item_form():
            flash("Form fields cannot be blank")
            return redirect(url_for('edit_item', category_id=category_id,
                                    item_id=item_id))
        item.name = request.form['name']
        item.description = request.form['description']
        item.short_description = request.form['short_description']
        item.price = request.form['price']
        item.category_id = request.form['category_id']
        item.save_image(request.files['image_file'])
        catalog.add(item)
        catalog.commit()
        flash("Item saved: %s" % item.name)
        return redirect(url_for('show_item', category_id=item.category_id,
                                item_id=item.id))
    else:
        return render_template('edit_item.html', item=item)


# Delete an item.
@app.route('/<category_id>/<item_id>/delete', methods=['GET', 'POST'])
def delete_item(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    if not allowed_to_change_item(item):
        return redirect(url_for('show_item', category_id=category_id,
                                item_id=item_id))
    if request.method == 'POST':
        item.delete_image()
        catalog.delete(item)
        catalog.commit()
        flash("Item deleted: %s" % item.name)
        return redirect(url_for('show_items', category_id=item.category_id))
    else:
        return render_template('delete_item.html', item=item)


# User Management page.
@app.route('/user-management/', methods=['GET', 'POST'])
def user_management():
    if not admin_rights():
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
                user.group = request.form[user.email]
                catalog.add(user)
        catalog.commit()
        flash("User settings have been saved")
        return redirect(url_for('user_management'))
    else:
        return render_template('user_management.html', users=users)


# Serve an item image.
@app.route('/img/<filename>')
def serve_image(filename):
    return send_from_directory(ITEM_IMAGE_DIRECTORY, filename)


# JSON endpoint for the whole catalog.
@app.route('/catalog.json')
def show_all_items_json():
    items = (
        catalog.query(Item)
            .order_by(Item.category_id)
            .order_by(Item.name)
            .all()
    )
    return jsonify(Items=[i.serialize for i in items])


# JSON endpoint for a category.
@app.route('/<category_id>.json')
def show_items_json(category_id):
    category = get_category_or_abort(category_id)
    items = (
        catalog.query(Item)
            .filter_by(category_id=category.id)
            .order_by(Item.name)
            .all()
    )
    return jsonify(Items=[i.serialize for i in items])


# JSON endpoint for an item.
@app.route('/<category_id>/<item_id>.json')
def show_item_json(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return jsonify(Item=item.serialize)


# XML endpoint for the whole catalog.
@app.route('/catalog.xml')
def show_all_items_xml():
    items = (
        catalog.query(Item)
            .order_by(Item.category_id)
            .order_by(Item.name)
            .all()
    )
    return xmlify(items)


# XML endpoint for a category.
@app.route('/<category_id>.xml')
def show_items_xml(category_id):
    category = get_category_or_abort(category_id)
    items = (
        catalog.query(Item)
            .filter_by(category_id=category.id)
            .order_by(Item.name)
            .all()
    )
    return xmlify(items)


# XML endpoint for an item.
@app.route('/<category_id>/<item_id>.xml')
def show_item_xml(category_id, item_id):
    item = get_item_or_abort(item_id, category_id)
    return xmlify([item])


# User sign-in, using Google API.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    code = request.form.get('code')
    try:
        # Upgrade the authorization code into a credentials object.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
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
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    if get_user_info(session['user_id']).group == 'readonly':
        flash("Access is restricted to read-only until account is approved by "
              "administrators")
    return "Login successful."


# User sign-out, using Google API.
@app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    # Only disconnect a connected user.
    access_token = session.get('credentials')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP GET request to revoke current token.
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


# Run the application.
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
