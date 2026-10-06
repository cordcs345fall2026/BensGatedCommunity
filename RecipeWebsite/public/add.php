<?php
declare(strict_types=1);
require __DIR__ . '/../app/lib.php';

// Add a recipe. GET shows the form; POST checks it and saves it.

$fields = ['title', 'category', 'description', 'prep_minutes', 'cook_minutes', 'servings', 'ingredients', 'instructions'];
$values = array_fill_keys($fields, '');
$errors = [];

/** A whole number within a range, or null. */
function whole_number(string $text, int $min, int $max): ?int
{
    if (preg_match('/^[0-9]{1,4}$/', $text) !== 1) {
        return null;
    }
    $number = (int) $text;
    return $number >= $min && $number <= $max ? $number : null;
}

function field_error(array $errors, string $name): void
{
    if (isset($errors[$name])) {
        echo '<p class="error">' . e($errors[$name]) . '</p>';
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    require_same_origin();
    foreach ($fields as $field) {
        $values[$field] = text_input($_POST, $field);
    }
    // Single-line fields: fold any line breaks into spaces.
    $values['title'] = str_replace("\n", ' ', $values['title']);
    $values['description'] = str_replace("\n", ' ', $values['description']);

    if (length($values['title']) < 3 || length($values['title']) > 100) {
        $errors['title'] = 'Enter a name between 3 and 100 characters.';
    }
    if (!in_array($values['category'], CATEGORIES, true)) {
        $errors['category'] = 'Choose a category from the list.';
    }
    if ($values['description'] === '' || length($values['description']) > 300) {
        $errors['description'] = 'Enter a description of up to 300 characters.';
    }
    $prep = whole_number($values['prep_minutes'], 0, 1440);
    $cook = whole_number($values['cook_minutes'], 0, 1440);
    $servings = whole_number($values['servings'], 1, 100);
    if ($prep === null) {
        $errors['prep_minutes'] = 'Enter minutes as a whole number from 0 to 1440.';
    }
    if ($cook === null) {
        $errors['cook_minutes'] = 'Enter minutes as a whole number from 0 to 1440.';
    }
    if ($servings === null) {
        $errors['servings'] = 'Enter a whole number from 1 to 100.';
    }
    if ($values['ingredients'] === '' || length($values['ingredients']) > 2000) {
        $errors['ingredients'] = 'List the ingredients, one per line, in up to 2,000 characters.';
    }
    if ($values['instructions'] === '' || length($values['instructions']) > 4000) {
        $errors['instructions'] = 'Write the steps, one per line, in up to 4,000 characters.';
    }

    if (!$errors) {
        $limit = (int) (config()['max_recipes'] ?? 500);
        $total = (int) db()->query('SELECT COUNT(*) FROM recipes')->fetchColumn();
        if ($total >= $limit) {
            $errors['form'] = 'The recipe box is full (' . $limit . ' recipes). Remove one before adding another.';
        }
    }

    if (!$errors) {
        $insert = db()->prepare(
            'INSERT INTO recipes
               (title, description, category, prep_minutes, cook_minutes, servings, ingredients, instructions)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        );
        $insert->execute([
            $values['title'], $values['description'], $values['category'],
            $prep, $cook, $servings, $values['ingredients'], $values['instructions'],
        ]);
        header('Location: recipe.php?id=' . (int) db()->lastInsertId() . '&added=1', true, 303);
        exit;
    }
    http_response_code(422);
}

page_top('Add a recipe');
?>
<h1>Add a recipe</h1>
<?php if ($errors): ?>
<p class="error" role="alert"><?= e($errors['form'] ?? 'The recipe was not saved. Fix the fields marked below and try again.') ?></p>
<?php endif; ?>

<form class="card" action="add.php" method="post">
  <label for="title">Recipe name</label>
  <input id="title" name="title" value="<?= e($values['title']) ?>" required minlength="3" maxlength="100">
  <?php field_error($errors, 'title'); ?>

  <label for="category">Category</label>
  <select id="category" name="category" required>
    <option value="">Choose one</option>
<?php foreach (CATEGORIES as $category): ?>
    <option<?= $values['category'] === $category ? ' selected' : '' ?>><?= e($category) ?></option>
<?php endforeach; ?>
  </select>
  <?php field_error($errors, 'category'); ?>

  <label for="description">Short description</label>
  <input id="description" name="description" value="<?= e($values['description']) ?>" required maxlength="300">
  <?php field_error($errors, 'description'); ?>

  <div class="row">
    <div>
      <label for="prep_minutes">Prep minutes</label>
      <input id="prep_minutes" name="prep_minutes" type="number" min="0" max="1440" value="<?= e($values['prep_minutes']) ?>" required>
      <?php field_error($errors, 'prep_minutes'); ?>
    </div>
    <div>
      <label for="cook_minutes">Cook minutes</label>
      <input id="cook_minutes" name="cook_minutes" type="number" min="0" max="1440" value="<?= e($values['cook_minutes']) ?>" required>
      <?php field_error($errors, 'cook_minutes'); ?>
    </div>
    <div>
      <label for="servings">Servings</label>
      <input id="servings" name="servings" type="number" min="1" max="100" value="<?= e($values['servings']) ?>" required>
      <?php field_error($errors, 'servings'); ?>
    </div>
  </div>

  <label for="ingredients">Ingredients, one per line</label>
  <textarea id="ingredients" name="ingredients" rows="6" required maxlength="2000"><?= e($values['ingredients']) ?></textarea>
  <?php field_error($errors, 'ingredients'); ?>

  <label for="instructions">Steps, one per line</label>
  <textarea id="instructions" name="instructions" rows="8" required maxlength="4000"><?= e($values['instructions']) ?></textarea>
  <?php field_error($errors, 'instructions'); ?>

  <p class="actions">
    <button type="submit">Add recipe</button>
    <a href="index.php">Cancel</a>
  </p>
</form>
<?php
page_bottom();
