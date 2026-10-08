<?php
declare(strict_types=1);
require __DIR__ . '/../app/lib.php';

// One recipe.

$find = db()->prepare(
    'SELECT id, title, description, category, prep_minutes, cook_minutes, servings,
            ingredients, instructions, is_starter
     FROM recipes WHERE id = ?'
);
$find->execute([recipe_id($_GET)]);
$recipe = $find->fetch();
if (!$recipe) {
    fail(404, 'That recipe does not exist. It may have been removed.');
}

$protected = !empty(config()['protect_starter_recipes']) && (int) $recipe['is_starter'] === 1;

page_top($recipe['title']);
?>
<?php if (isset($_GET['added'])): ?>
<p class="notice" role="status">Recipe added.</p>
<?php endif; ?>

<article class="card">
  <h1><?= e($recipe['title']) ?></h1>
  <p class="lead"><?= e($recipe['description']) ?></p>

  <dl class="facts">
    <div><dt>Category</dt><dd><?= e($recipe['category']) ?></dd></div>
    <div><dt>Prep</dt><dd><?= (int) $recipe['prep_minutes'] ?> min</dd></div>
    <div><dt>Cook</dt><dd><?= (int) $recipe['cook_minutes'] ?> min</dd></div>
    <div><dt>Serves</dt><dd><?= (int) $recipe['servings'] ?></dd></div>
  </dl>

  <h2>Ingredients</h2>
  <ul class="ruled">
<?php foreach (lines($recipe['ingredients']) as $ingredient): ?>
    <li><?= e($ingredient) ?></li>
<?php endforeach; ?>
  </ul>

  <h2>Steps</h2>
  <ol class="ruled">
<?php foreach (lines($recipe['instructions']) as $step): ?>
    <li><?= e($step) ?></li>
<?php endforeach; ?>
  </ol>
</article>

<p class="actions">
  <a href="index.php">Back to all recipes</a>
<?php if ($protected): ?>
  <span class="muted">Starter recipes can&rsquo;t be removed. Recipes added through the site can.</span>
<?php else: ?>
  <a class="danger" href="delete.php?id=<?= (int) $recipe['id'] ?>">Remove this recipe</a>
<?php endif; ?>
</p>
<?php
page_bottom();
