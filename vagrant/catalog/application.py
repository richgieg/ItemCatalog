from flask import Flask, render_template
app = Flask(__name__)


@app.context_processor
def inject_navigation():
    return dict(navigation = ("one", "two", "three"))


@app.route('/')
def show_main():
    return render_template('show_main.html')


@app.route('/<string:category_id>/')
def show_items(category_id):
    return render_template('show_items.html', category_id = category_id)


@app.route('/<string:category_id>/<string:item_id>')
def show_item(category_id, item_id):
    return render_template('show_item.html', category_id = category_id,
                           item_id = item_id)


@app.route('/items/new')
def new_item():
    return render_template('new_item.html')


@app.route('/items/<string:item_id>/edit')
def edit_item(item_id):
    return render_template('edit_item.html', item_id = item_id)


@app.route('/items/<string:item_id>/delete')
def delete_item(item_id):
    return render_template('delete_item.html', item_id = item_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)