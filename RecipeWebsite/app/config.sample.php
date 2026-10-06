<?php
// Copy this file to config.php on the server and put the real password in.
// config.php is ignored by git, so the password never reaches the repository.

return [
    // Same machine as the web server. For a separate database server use
    // 'mysql:host=10.0.0.5;port=3306;dbname=recipes;charset=utf8mb4'.
    'dsn'      => 'mysql:host=localhost;dbname=recipes;charset=utf8mb4',
    'user'     => 'recipes_web',
    'password' => 'CHANGE-ME',

    // There is no login, so anyone who can reach the site can use the Remove
    // button. With this on, the recipes loaded from db/seed.sql cannot be
    // removed; only recipes added through the site can. Set it to false to
    // make every recipe removable.
    'protect_starter_recipes' => true,

    // Add is refused once the table holds this many recipes, so a script
    // cannot fill the database.
    'max_recipes' => 500,
];
