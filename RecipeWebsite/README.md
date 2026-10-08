# Recipe Box

A small recipe website for the CSC 345 red team / blue team hackathons.
Every page is built from a MySQL table. Visitors can browse and search
recipes, add a recipe, and remove a recipe. There is no login.

## How it works

- nginx serves the `public/` folder and passes the four `.php` pages to PHP.
- Each page runs its MySQL query and prints plain HTML. There is no JavaScript.
- `app/` (shared code and the database password) sits outside the web root.

| Path | What it is |
| --- | --- |
| `public/index.php` | Recipe list and search |
| `public/recipe.php` | One recipe |
| `public/add.php` | Add-a-recipe form |
| `public/delete.php` | Remove a recipe, after a confirmation page |
| `public/style.css` | The only static file |
| `app/lib.php` | Database connection, HTML escaping, page header and footer |
| `app/config.sample.php` | Template for `app/config.php`, which holds the password |
| `db/schema.sql`, `db/seed.sql` | The `recipes` table and 99 starter recipes |
| `deploy/nginx-recipes.conf` | The nginx site |

## Set up on Ubuntu

Run these from this `RecipeWebsite` folder on the server.

```bash
sudo apt update
sudo apt install -y nginx mysql-server php-fpm php-mysql
```

Copy the site into place:

```bash
sudo mkdir -p /var/www/recipes
sudo cp -r public app /var/www/recipes/
```

Create the database and load the recipes:

```bash
sudo mysql -e "CREATE DATABASE recipes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
sudo mysql --default-character-set=utf8mb4 recipes < db/schema.sql
sudo mysql --default-character-set=utf8mb4 recipes < db/seed.sql
```

Make a password, then create the site's database account with it. The
account can read, add and delete rows in the one table and nothing else.

```bash
openssl rand -hex 24
```

```bash
sudo mysql
```

```sql
CREATE USER 'recipes_web'@'localhost' IDENTIFIED BY 'paste-the-password-here';
GRANT SELECT, INSERT, DELETE ON recipes.recipes TO 'recipes_web'@'localhost';
EXIT;
```

Give the site the same password:

```bash
sudo cp app/config.sample.php /var/www/recipes/app/config.php
sudo nano /var/www/recipes/app/config.php
sudo chown root:www-data /var/www/recipes/app/config.php
sudo chmod 640 /var/www/recipes/app/config.php
```

Turn on the nginx site:

```bash
sudo cp deploy/nginx-recipes.conf /etc/nginx/sites-available/recipes
sudo ln -sf /etc/nginx/sites-available/recipes /etc/nginx/sites-enabled/recipes
sudo rm -f /etc/nginx/sites-enabled/default
ls /run/php/
sudo nginx -t && sudo systemctl reload nginx
```

If `ls /run/php/` shows no `php-fpm.sock`, edit the two `fastcgi_pass` lines
in `/etc/nginx/sites-available/recipes` to the versioned socket it does show
(for example `php8.3-fpm.sock`), then run the last line again.

Open `http://<server address>/` from another machine. You should see the
recipe list.

## What was and wasn't tested

The pages were run on PHP 8.3 against MySQL 8.0 on a Windows laptop: list,
search, paging, add, remove, and the starter-recipe protection all worked.
The nginx file and the Ubuntu commands above have not been run anywhere yet,
so read `sudo nginx -t` carefully the first time.

## No login: what that means

Anyone who can reach the site can use Add and Remove. Three things limit the
damage:

- **Starter recipes can't be removed.** The 99 recipes from `db/seed.sql`
  are marked `is_starter`, and the Remove page refuses them. Recipes added
  through the site can be removed by anyone. To make every recipe removable,
  set `protect_starter_recipes` to `false` in `config.php`.
- **Adding stops at 500 recipes** (`max_recipes` in `config.php`), and nginx
  allows each address 10 form posts a minute.
- **You can limit Add and Remove to your own machines.** Uncomment the
  `allow` / `deny` lines in `deploy/nginx-recipes.conf` and list your
  addresses. Everyone else can still browse.

To clear out junk recipes and get back to the starter set:

```bash
sudo mysql recipes -e "DELETE FROM recipes WHERE is_starter = 0"
```

## What is already locked down

- **SQL injection:** every query is a prepared statement; visitor input is
  never pasted into SQL.
- **Cross-site scripting:** everything printed from the database is escaped,
  the site has no JavaScript, and a Content-Security-Policy header tells
  browsers to run none.
- **Database account:** `SELECT`, `INSERT` and `DELETE` on one table. It
  cannot drop tables, read other databases, or read and write files.
- **Removing needs a form post.** A link or image tag cannot delete a
  recipe, and posts sent from other websites are refused.
- **Errors:** visitors get a generic message; details go to the server log.
- **nginx:** only the four pages run as PHP, dotfiles such as `.git` return
  404, uploads are impossible (16 KB request limit, no upload code), and the
  nginx version is hidden.

## Server checklist

The site can only be as safe as the machine it runs on.

- Confirm MySQL listens on localhost only: `sudo ss -ltnp | grep 3306`
  should show `127.0.0.1`, not `0.0.0.0`.
- Run `sudo mysql_secure_installation`.
- Firewall: `sudo ufw allow OpenSSH`, `sudo ufw allow 80/tcp`, then
  `sudo ufw enable`.
- SSH: strong passwords or keys only, and no root login.
- Keep packages current: `sudo apt update && sudo apt upgrade`.
- If the earlier Flask version of this site is still running on the server,
  stop and remove it. It ran in debug mode and shipped a demo account with a
  known password.
