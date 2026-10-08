"""Recipe Box API: the only code that talks to MySQL.

The pages in public/ are plain HTML. Their script (public/app.js) calls the
four routes below, and nginx passes anything under /api/ to this program.

    python3 server.py

This folder sits outside the web root (public/), so the web server can never
serve these files directly.
"""
import math
import re
from pathlib import Path

import pymysql
from flask import Flask, abort, g, jsonify, request
from waitress import serve
from werkzeug.exceptions import HTTPException

try:
    import config
except ImportError:
    raise SystemExit('app/config.py is missing; copy config.sample.py to config.py')

# The same list is in the Category menu in public/add.html.
CATEGORIES = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Snack', 'Soup', 'Salad', 'Beverage', 'Other']
FIELDS = ['title', 'category', 'description', 'prep_minutes', 'cook_minutes', 'servings', 'ingredients', 'instructions']
PER_PAGE = 20

# nginx serves public/ on the server. Serving it from here as well means
# "python3 server.py" on its own is enough to try the site on a laptop.
PUBLIC = Path(__file__).resolve().parent.parent / 'public'

app = Flask(__name__, static_folder=str(PUBLIC), static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024


def db():
    """One MySQL connection per request, closed when the request ends."""
    if 'db' not in g:
        g.db = pymysql.connect(
            charset='utf8mb4',
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
            **config.DATABASE
        )
    return g.db


@app.teardown_appcontext
def close_db(error):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()


@app.after_request
def security_headers(response):
    # Scripts, styles and API calls may only come from this site itself.
    # deploy/nginx-recipes.conf sends the same headers with the static files.
    response.headers['Content-Security-Policy'] = (
        "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
        "connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.description), error.code


@app.errorhandler(Exception)
def server_error(error):
    # Details go to the server log, never to visitors.
    app.logger.exception('recipes: %s', error)
    return jsonify(error='Something went wrong on the server. Try again in a minute.'), 500


def clean(value):
    """A cleaned-up string from the visitor. Anything that is not valid text becomes ''."""
    if not isinstance(value, str):
        return ''
    try:
        value.encode('utf-8')
    except UnicodeEncodeError:
        return ''
    value = value.replace('\r\n', '\n').replace('\r', '\n').replace('\t', ' ')
    value = re.sub(r'[\x00-\x09\x0b-\x1f\x7f]', '', value)  # control characters
    return value.strip()


def whole_number(text, low, high):
    """A whole number within a range, or None."""
    if not re.fullmatch(r'[0-9]{1,4}', text):
        return None
    number = int(text)
    return number if low <= number <= high else None


def require_same_origin():
    """Refuse a request that another website sent the visitor's browser to make."""
    origin = request.headers.get('Origin', '')
    if origin and origin not in ('http://' + request.host, 'https://' + request.host):
        abort(403, 'That request was not sent from this site.')


def find_recipe(recipe_id):
    with db().cursor() as cursor:
        cursor.execute(
            'SELECT id, title, description, category, prep_minutes, cook_minutes, servings,'
            ' ingredients, instructions, is_starter FROM recipes WHERE id = %s',
            [recipe_id],
        )
        recipe = cursor.fetchone()
    if recipe is None:
        abort(404, 'That recipe does not exist. It may have been removed.')
    recipe['removable'] = not (config.PROTECT_STARTER_RECIPES and recipe.pop('is_starter') == 1)
    return recipe


@app.route('/')
def home():
    return app.send_static_file('index.html')


@app.route('/api/recipes', methods=['GET'])
def list_recipes():
    """Recipe list, newest first, with an optional search."""
    search = clean(request.args.get('q', ''))
    if len(search) > 100:
        search = ''
    page = request.args.get('page', '')
    page = int(page) if re.fullmatch(r'[1-9][0-9]{0,3}', page) else 1

    where, params = '', []
    if search:
        # "|" is the LIKE escape character here, so %, _ and | typed into the
        # search box match themselves instead of acting as wildcards.
        like = '%' + search.replace('|', '||').replace('%', '|%').replace('_', '|_') + '%'
        where = " WHERE title LIKE %s ESCAPE '|' OR description LIKE %s ESCAPE '|' OR ingredients LIKE %s ESCAPE '|'"
        params = [like, like, like]

    with db().cursor() as cursor:
        cursor.execute('SELECT COUNT(*) AS total FROM recipes' + where, params)
        total = cursor.fetchone()['total']
        pages = max(1, math.ceil(total / PER_PAGE))
        page = min(page, pages)
        cursor.execute(
            'SELECT id, title, description, category FROM recipes' + where
            + ' ORDER BY id DESC LIMIT %s OFFSET %s',
            params + [PER_PAGE, (page - 1) * PER_PAGE],
        )
        recipes = cursor.fetchall()
    return jsonify(recipes=recipes, total=total, page=page, pages=pages, search=search)


@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def show_recipe(recipe_id):
    """One recipe."""
    return jsonify(find_recipe(recipe_id))


@app.route('/api/recipes', methods=['POST'])
def add_recipe():
    """Add a recipe. Answers with its new id, or with a message for each field that is wrong."""
    require_same_origin()
    # Only JSON is accepted, which a form on another website cannot send.
    data = request.get_json(silent=True) if request.is_json else None
    if not isinstance(data, dict):
        abort(400, 'Send the recipe as JSON.')

    values = {field: clean(data.get(field)) for field in FIELDS}
    # Single-line fields: fold any line breaks into spaces.
    values['title'] = values['title'].replace('\n', ' ')
    values['description'] = values['description'].replace('\n', ' ')

    errors = {}
    if not 3 <= len(values['title']) <= 100:
        errors['title'] = 'Enter a name between 3 and 100 characters.'
    if values['category'] not in CATEGORIES:
        errors['category'] = 'Choose a category from the list.'
    if not 1 <= len(values['description']) <= 300:
        errors['description'] = 'Enter a description of up to 300 characters.'
    prep = whole_number(values['prep_minutes'], 0, 1440)
    cook = whole_number(values['cook_minutes'], 0, 1440)
    servings = whole_number(values['servings'], 1, 100)
    if prep is None:
        errors['prep_minutes'] = 'Enter minutes as a whole number from 0 to 1440.'
    if cook is None:
        errors['cook_minutes'] = 'Enter minutes as a whole number from 0 to 1440.'
    if servings is None:
        errors['servings'] = 'Enter a whole number from 1 to 100.'
    if not 1 <= len(values['ingredients']) <= 2000:
        errors['ingredients'] = 'List the ingredients, one per line, in up to 2,000 characters.'
    if not 1 <= len(values['instructions']) <= 4000:
        errors['instructions'] = 'Write the steps, one per line, in up to 4,000 characters.'

    with db().cursor() as cursor:
        if not errors:
            cursor.execute('SELECT COUNT(*) AS total FROM recipes')
            if cursor.fetchone()['total'] >= config.MAX_RECIPES:
                errors['form'] = 'The recipe box is full (%d recipes). Remove one before adding another.' % config.MAX_RECIPES
        if errors:
            return jsonify(errors=errors), 422
        cursor.execute(
            'INSERT INTO recipes'
            ' (title, description, category, prep_minutes, cook_minutes, servings, ingredients, instructions)'
            ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            [values['title'], values['description'], values['category'],
             prep, cook, servings, values['ingredients'], values['instructions']],
        )
        return jsonify(id=cursor.lastrowid), 201


@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def remove_recipe(recipe_id):
    """Remove a recipe. Browsers only send DELETE from this site's own script."""
    require_same_origin()
    if not find_recipe(recipe_id)['removable']:
        abort(403, 'Starter recipes can’t be removed. Recipes added through the site can.')
    with db().cursor() as cursor:
        # The is_starter condition repeats the check above inside the query itself.
        cursor.execute(
            'DELETE FROM recipes WHERE id = %s' + (' AND is_starter = 0' if config.PROTECT_STARTER_RECIPES else ''),
            [recipe_id],
        )
    return '', 204


if __name__ == '__main__':
    serve(app, host=config.LISTEN_HOST, port=config.LISTEN_PORT)
