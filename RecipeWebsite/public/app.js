// Recipe Box pages. The HTML files are static; this script fills them in
// from the API (app/server.py), which is the only code that talks to MySQL.
//
// Everything that came from the database is put on the page with
// textContent, never innerHTML, so a recipe cannot add markup or script.
'use strict';

const query = new URLSearchParams(location.search);
const byId = (id) => document.getElementById(id);
const NO_ANSWER = 'The recipe server did not answer. Try again in a minute.';

/** Call the API. Resolves to { ok, status, body }, where body is the JSON it sent back. */
async function api(path, options) {
  try {
    const response = await fetch('api/' + path, options);
    const body = response.status === 204 ? {} : await response.json();
    return { ok: response.ok, status: response.status, body };
  } catch (error) {
    // The API is down, or nginx answered for it with a page that is not JSON.
    return { ok: false, status: 0, body: { error: NO_ANSWER } };
  }
}

/** A new element holding plain text. */
function element(tag, text, properties) {
  const node = document.createElement(tag);
  node.textContent = text;
  return Object.assign(node, properties);
}

/** Show an error in place of the page. */
function fail(message) {
  const back = element('p', '');
  back.append(element('a', 'Back to all recipes', { href: 'index.html' }));
  document.title = 'Problem - Recipe Box';
  document.querySelector('main').replaceChildren(
    element('h1', 'That didn’t work'),
    element('p', message || NO_ANSWER),
    back
  );
}

/** Swap the "Loading" line for the page content. */
function ready() {
  byId('status').remove();
  byId('content').hidden = false;
}

/** The recipe id in the page address, or 0 when it is not a plain positive number. */
function recipeId() {
  const id = query.get('id') || '';
  return /^[1-9][0-9]{0,9}$/.test(id) ? Number(id) : 0;
}

/** Fetch the recipe named in the page address. Shows an error and gives null if there is none. */
async function loadRecipe() {
  const { ok, body } = await api('recipes/' + recipeId());
  if (!ok) {
    fail(body.error);
    return null;
  }
  return body;
}

/** Split stored text into its non-empty lines. */
function lines(text) {
  return text.split('\n').map((line) => line.trim()).filter(Boolean);
}

function pageLink(search, page) {
  const params = new URLSearchParams();
  if (search) params.set('q', search);
  if (page > 1) params.set('page', page);
  const text = params.toString();
  return 'index.html' + (text ? '?' + text : '');
}

// index.html: recipe list, newest first, with an optional search.
async function listPage() {
  byId('removed').hidden = !query.has('removed');

  const params = new URLSearchParams();
  for (const name of ['q', 'page']) {
    if (query.get(name)) params.set(name, query.get(name));
  }
  const { ok, body } = await api('recipes?' + params);
  if (!ok) return fail(body.error);
  const { recipes, total, page, pages, search } = body;

  byId('q').value = search;
  if (search) {
    document.title = 'Search results - Recipe Box';
    byId('heading').textContent = 'Results for “' + search + '”';
    byId('summary').replaceChildren(total + ' found. ', element('a', 'Show all recipes', { href: 'index.html' }));
    byId('empty').hidden = recipes.length > 0;
  } else {
    byId('summary').textContent = total + ' in the box, newest first.';
  }

  for (const recipe of recipes) {
    const item = element('li', '');
    item.append(
      element('a', recipe.title, { href: 'recipe.html?id=' + recipe.id }),
      element('span', recipe.category, { className: 'category' }),
      element('p', recipe.description)
    );
    byId('recipes').append(item);
  }
  byId('recipes').hidden = recipes.length === 0;

  if (pages > 1) {
    const nav = byId('pages');
    if (page > 1) nav.append(element('a', 'Newer recipes', { href: pageLink(search, page - 1) }));
    nav.append(element('span', 'Page ' + page + ' of ' + pages));
    if (page < pages) nav.append(element('a', 'Older recipes', { href: pageLink(search, page + 1) }));
    nav.hidden = false;
  }
}

// recipe.html: one recipe.
async function recipePage() {
  const recipe = await loadRecipe();
  if (!recipe) return;

  byId('added').hidden = !query.has('added');
  document.title = recipe.title + ' - Recipe Box';
  byId('title').textContent = recipe.title;
  byId('description').textContent = recipe.description;
  byId('category').textContent = recipe.category;
  byId('prep').textContent = recipe.prep_minutes + ' min';
  byId('cook').textContent = recipe.cook_minutes + ' min';
  byId('servings').textContent = recipe.servings;
  byId('ingredients').append(...lines(recipe.ingredients).map((line) => element('li', line)));
  byId('instructions').append(...lines(recipe.instructions).map((line) => element('li', line)));

  byId('remove').href = 'delete.html?id=' + recipe.id;
  byId('remove').hidden = !recipe.removable;
  byId('protected').hidden = recipe.removable;
  ready();
}

// add.html: send the form to the API, then show the new recipe or what to fix.
function addPage() {
  const form = byId('add-form');
  const button = form.querySelector('button');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    button.disabled = true;
    const { status, body } = await api('recipes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.fromEntries(new FormData(form))),
    });
    if (status === 201) {
      location.href = 'recipe.html?id=' + body.id + '&added=1';
      return;
    }
    button.disabled = false;

    // A message under each field the API refused, and one above the form.
    const errors = body.errors || { form: body.error || NO_ANSWER };
    form.querySelectorAll('p.error').forEach((message) => message.remove());
    for (const [name, message] of Object.entries(errors)) {
      const field = form.elements[name];
      if (field) field.after(element('p', message, { className: 'error' }));
    }
    const summary = byId('form-error');
    summary.textContent = errors.form || 'The recipe was not saved. Fix the fields marked below and try again.';
    summary.hidden = false;
    summary.scrollIntoView();
  });
}

// delete.html: ask for confirmation; nothing is removed until the button is pressed.
async function removePage() {
  const recipe = await loadRecipe();
  if (!recipe) return;
  if (!recipe.removable) return fail('Starter recipes can’t be removed. Recipes added through the site can.');

  byId('heading').textContent = 'Remove “' + recipe.title + '”?';
  byId('keep').href = 'recipe.html?id=' + recipe.id;
  ready();

  const form = byId('remove-form');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    form.querySelector('button').disabled = true;
    const { ok, body } = await api('recipes/' + recipe.id, { method: 'DELETE' });
    if (!ok) return fail(body.error);
    location.href = 'index.html?removed=1';
  });
}

const pages = { list: listPage, recipe: recipePage, add: addPage, remove: removePage };
pages[document.body.dataset.page]();
