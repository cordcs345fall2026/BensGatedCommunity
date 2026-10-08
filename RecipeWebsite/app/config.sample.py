# Copy this file to config.py on the server and put the real password in.
# config.py is ignored by git, so the password never reaches the repository.

# Same machine as the web server. For a separate database server, change
# host to its address, for example '10.0.0.5'.
DATABASE = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'recipes_web',
    'password': 'CHANGE-ME',
    'database': 'recipes',
}

# There is no login, so anyone who can reach the site can use the Remove
# button. With this on, the recipes loaded from db/seed.sql cannot be
# removed; only recipes added through the site can. Set it to False to
# make every recipe removable.
PROTECT_STARTER_RECIPES = True

# Add is refused once the table holds this many recipes, so a script
# cannot fill the database.
MAX_RECIPES = 500

# Where the API listens. nginx passes /api/ requests here. Keep it on
# 127.0.0.1 so nothing outside the server can reach it directly.
LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 8000
