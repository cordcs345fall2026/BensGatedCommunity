<?php
declare(strict_types=1);

// Shared code for every page. This folder sits outside the web root
// (public/), so the web server can never serve or run these files directly.

ini_set('display_errors', '0');  // errors go to the server log, never to visitors
error_reporting(E_ALL);
ob_start();

header_remove('X-Powered-By');
// The site uses no JavaScript, and this policy tells browsers to refuse any.
header("Content-Security-Policy: default-src 'none'; style-src 'self'; img-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'");
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: same-origin');

const CATEGORIES = ['Breakfast', 'Lunch', 'Dinner', 'Dessert', 'Snack', 'Soup', 'Salad', 'Beverage', 'Other'];
const PER_PAGE = 20;

set_exception_handler(function (Throwable $error): void {
    error_log('recipes: ' . get_class($error) . ': ' . $error->getMessage());
    fail(500, 'Something went wrong on the server. Try again in a minute.');
});

function config(): array
{
    static $config = null;
    if ($config === null) {
        $file = __DIR__ . '/config.php';
        if (!is_file($file)) {
            throw new RuntimeException('app/config.php is missing; copy config.sample.php');
        }
        $config = require $file;
    }
    return $config;
}

function db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $config = config();
        // This constant was renamed in PHP 8.4; use whichever name this PHP has.
        $multiStatements = defined('Pdo\Mysql::ATTR_MULTI_STATEMENTS')
            ? constant('Pdo\Mysql::ATTR_MULTI_STATEMENTS')
            : PDO::MYSQL_ATTR_MULTI_STATEMENTS;
        $pdo = new PDO($config['dsn'], $config['user'], $config['password'], [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,  // real prepared statements
            $multiStatements             => false,  // one statement per query
        ]);
    }
    return $pdo;
}

/** Escape text for HTML. Everything that came from the database or a visitor goes through this. */
function e(string $text): string
{
    return htmlspecialchars($text, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

/** A cleaned-up string from $_GET or $_POST. Arrays and invalid UTF-8 become ''. */
function text_input(array $source, string $name): string
{
    $value = $source[$name] ?? '';
    if (!is_string($value) || preg_match('//u', $value) !== 1) {
        return '';
    }
    $value = str_replace(["\r\n", "\r", "\t"], ["\n", "\n", ' '], $value);
    $value = preg_replace('/[\x00-\x09\x0B-\x1F\x7F]/', '', $value);  // control characters
    return trim($value);
}

/** Length in characters, not bytes. */
function length(string $text): int
{
    return (int) preg_match_all('/./us', $text);
}

/** A recipe id from $_GET or $_POST, or 0 when it is not a plain positive number. */
function recipe_id(array $source): int
{
    $value = $source['id'] ?? '';
    if (!is_string($value) || preg_match('/^[1-9][0-9]{0,9}$/', $value) !== 1) {
        return 0;
    }
    return (int) $value;
}

/** Split stored text into its non-empty lines. */
function lines(string $text): array
{
    return array_values(array_filter(array_map('trim', explode("\n", $text)), 'strlen'));
}

/** Refuse a form post that another website sent the visitor's browser to make. */
function require_same_origin(): void
{
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    $host = $_SERVER['HTTP_HOST'] ?? '';
    if ($origin !== '' && $origin !== 'http://' . $host && $origin !== 'https://' . $host) {
        fail(403, 'That form was not sent from this site.');
    }
}

function page_top(string $title): void
{
    ?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= e($title) ?> - Recipe Box</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <a class="site-name" href="index.php">Recipe Box</a>
  <a class="button" href="add.php">Add a recipe</a>
</header>
<main>
<?php
}

function page_bottom(): void
{
    ?>
</main>
</body>
</html>
<?php
}

/** Show an error page and stop. */
function fail(int $status, string $message): void
{
    while (ob_get_level() > 0) {
        ob_end_clean();
    }
    http_response_code($status);
    page_top('Problem');
    echo '<h1>That didn&rsquo;t work</h1><p>' . e($message) . '</p>';
    echo '<p><a href="index.php">Back to all recipes</a></p>';
    page_bottom();
    exit;
}
