<?php
declare(strict_types=1);
require __DIR__ . '/../app/lib.php';

// Recipe list, newest first, with an optional search.

$search = text_input($_GET, 'q');
if (length($search) > 100) {
    $search = '';
}
$page = 1;
if (isset($_GET['page']) && is_string($_GET['page']) && preg_match('/^[1-9][0-9]{0,3}$/', $_GET['page']) === 1) {
    $page = (int) $_GET['page'];
}

$where = '';
$params = [];
if ($search !== '') {
    // "|" is the LIKE escape character here, so %, _ and | typed into the
    // search box match themselves instead of acting as wildcards.
    $like = '%' . str_replace(['|', '%', '_'], ['||', '|%', '|_'], $search) . '%';
    $where = " WHERE title LIKE ? ESCAPE '|' OR description LIKE ? ESCAPE '|' OR ingredients LIKE ? ESCAPE '|'";
    $params = [$like, $like, $like];
}

$count = db()->prepare('SELECT COUNT(*) FROM recipes' . $where);
$count->execute($params);
$total = (int) $count->fetchColumn();
$pages = max(1, (int) ceil($total / PER_PAGE));
$page = min($page, $pages);

$list = db()->prepare(
    'SELECT id, title, description, category FROM recipes' . $where . ' ORDER BY id DESC LIMIT ? OFFSET ?'
);
$position = 1;
foreach ($params as $value) {
    $list->bindValue($position++, $value);
}
$list->bindValue($position++, PER_PAGE, PDO::PARAM_INT);
$list->bindValue($position, ($page - 1) * PER_PAGE, PDO::PARAM_INT);
$list->execute();
$recipes = $list->fetchAll();

function page_link(string $search, int $page): string
{
    $query = $search === '' ? [] : ['q' => $search];
    if ($page > 1) {
        $query['page'] = $page;
    }
    return 'index.php' . ($query ? '?' . http_build_query($query) : '');
}

page_top($search === '' ? 'Recipes' : 'Search results');
?>
<form class="search" action="index.php" method="get" role="search">
  <label for="q">Search recipes</label>
  <input type="search" id="q" name="q" value="<?= e($search) ?>" maxlength="100">
  <button type="submit">Search</button>
</form>

<?php if (isset($_GET['removed'])): ?>
<p class="notice" role="status">Recipe removed.</p>
<?php endif; ?>

<?php if ($search !== ''): ?>
<h1>Results for &ldquo;<?= e($search) ?>&rdquo;</h1>
<p><?= $total ?> found. <a href="index.php">Show all recipes</a></p>
<?php else: ?>
<h1>All recipes</h1>
<p><?= $total ?> in the box, newest first.</p>
<?php endif; ?>

<?php if (!$recipes): ?>
<p>Nothing matches that search. Try a single ingredient, such as &ldquo;garlic&rdquo;.</p>
<?php else: ?>
<ul class="recipes">
<?php foreach ($recipes as $recipe): ?>
  <li>
    <a href="recipe.php?id=<?= (int) $recipe['id'] ?>"><?= e($recipe['title']) ?></a>
    <span class="category"><?= e($recipe['category']) ?></span>
    <p><?= e($recipe['description']) ?></p>
  </li>
<?php endforeach; ?>
</ul>
<?php endif; ?>

<?php if ($pages > 1): ?>
<nav class="pages" aria-label="Pages">
<?php if ($page > 1): ?>
  <a href="<?= e(page_link($search, $page - 1)) ?>">Newer recipes</a>
<?php endif; ?>
  <span>Page <?= $page ?> of <?= $pages ?></span>
<?php if ($page < $pages): ?>
  <a href="<?= e(page_link($search, $page + 1)) ?>">Older recipes</a>
<?php endif; ?>
</nav>
<?php endif; ?>
<?php
page_bottom();
