from flask import Flask
app = Flask(__name__)


@app.route('/')
def show_main():
    return "This is the main page"


@app.route('/<string:category_id>/')
def show_items(category_id):
    return "This will display category '%s'" % category_id


@app.route('/<string:category_id>/<string:item_id>')
def show_item(category_id, item_id):
    return "This will display item '%s' from category '%s'" % (item_id, category_id)


@app.route('/items/new')
def new_item():
    return "This is the new item page"


@app.route('/items/<string:item_id>/edit')
def edit_item(item_id):
    return "This is the edit page for '%s'" % item_id


@app.route('/items/<string:item_id>/delete')
def delete_item(item_id):
    return "This is the delete page for '%s'" % item_id


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)