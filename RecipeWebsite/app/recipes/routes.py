from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.models import Recipe
from app.recipes.forms import RecipeForm

recipes = Blueprint("recipes", __name__, url_prefix="/recipes")


@recipes.route("/")
def list_recipes():
    category = request.args.get("category", "")
    search = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Recipe.query
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Recipe.title.ilike(f"%{search}%"))

    pagination = query.order_by(Recipe.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template("recipes/list.html", pagination=pagination,
                           category=category, search=search, title="Recipes")


@recipes.route("/<int:recipe_id>")
def detail(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    ingredients = [i.strip() for i in recipe.ingredients.splitlines() if i.strip()]
    return render_template("recipes/detail.html", recipe=recipe,
                           ingredients=ingredients, title=recipe.title)


@recipes.route("/new", methods=["GET", "POST"])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        recipe = Recipe(
            title=form.title.data,
            description=form.description.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            prep_time=form.prep_time.data,
            cook_time=form.cook_time.data,
            servings=form.servings.data,
            category=form.category.data or None,
            user_id=current_user.id,
        )
        db.session.add(recipe)
        db.session.commit()
        flash("Recipe created!", "success")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))
    return render_template("recipes/form.html", form=form, title="New Recipe",
                           legend="Add Recipe")


@recipes.route("/<int:recipe_id>/edit", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)
    form = RecipeForm(obj=recipe)
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.description = form.description.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.category = form.category.data or None
        db.session.commit()
        flash("Recipe updated!", "success")
        return redirect(url_for("recipes.detail", recipe_id=recipe.id))
    return render_template("recipes/form.html", form=form, title="Edit Recipe",
                           legend="Edit Recipe")


@recipes.route("/<int:recipe_id>/delete", methods=["POST"])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash("Recipe deleted.", "info")
    return redirect(url_for("recipes.list_recipes"))
