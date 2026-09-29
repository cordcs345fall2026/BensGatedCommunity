from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Recipe

main = Blueprint("main", __name__)


@main.route("/")
def index():
    recent = Recipe.query.order_by(Recipe.created_at.desc()).limit(6).all()
    return render_template("main/index.html", recent=recent, title="Home")


@main.route("/profile")
@login_required
def profile():
    recipes = Recipe.query.filter_by(user_id=current_user.id)\
                          .order_by(Recipe.created_at.desc()).all()
    return render_template("main/profile.html", recipes=recipes, title="My Profile")
