<?php
declare(strict_types=1);
require __DIR__ . '/../app/lib.php';

// Remove a recipe. GET only asks for confirmation; nothing is removed
// unless the confirmation form is posted.

$posted = $_SERVER['REQUEST_METHOD'] === 'POST';
$id = recipe_id($posted ? $_POST : $_GET);

$find = db()->prepare('SELECT id, title, is_starter FROM recipes WHERE id = ?');
$find->execute([$id]);
$recipe = $find->fetch();
if (!$recipe) {
    fail(404, 'That recipe does not exist. It may already have been removed.');
}

$protect = !empty(config()['protect_starter_recipes']);
if ($protect && (int) $recipe['is_starter'] === 1) {
    fail(403, 'Starter recipes can’t be removed. Recipes added through the site can.');
}

if ($posted) {
    require_same_origin();
    // The is_starter condition repeats the check above inside the query itself.
    $delete = db()->prepare('DELETE FROM recipes WHERE id = ?' . ($protect ? ' AND is_starter = 0' : ''));
    $delete->execute([$id]);
    header('Location: index.php?removed=1', true, 303);
    exit;
}

page_top('Remove recipe');
?>
<h1>Remove &ldquo;<?= e($recipe['title']) ?>&rdquo;?</h1>
<p>This deletes the recipe from the database. It can&rsquo;t be undone.</p>
<form class="actions" action="delete.php" method="post">
  <input type="hidden" name="id" value="<?= (int) $recipe['id'] ?>">
  <button type="submit" class="danger">Remove recipe</button>
  <a href="recipe.php?id=<?= (int) $recipe['id'] ?>">Keep it</a>
</form>
<?php
page_bottom();
