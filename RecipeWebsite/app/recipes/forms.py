from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


CATEGORIES = [
    ("", "-- Select Category --"),
    ("Breakfast", "Breakfast"),
    ("Lunch", "Lunch"),
    ("Dinner", "Dinner"),
    ("Dessert", "Dessert"),
    ("Snack", "Snack"),
    ("Soup", "Soup"),
    ("Salad", "Salad"),
    ("Beverage", "Beverage"),
    ("Other", "Other"),
]


class RecipeForm(FlaskForm):
    title = StringField("Title",
                        validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description",
                                validators=[DataRequired(), Length(max=500)])
    ingredients = TextAreaField(
        "Ingredients (one per line)",
        validators=[DataRequired()],
    )
    instructions = TextAreaField("Instructions",
                                 validators=[DataRequired()])
    prep_time = IntegerField("Prep Time (minutes)",
                             validators=[Optional(),
                                         NumberRange(min=0, max=9999)])
    cook_time = IntegerField("Cook Time (minutes)",
                             validators=[Optional(),
                                         NumberRange(min=0, max=9999)])
    servings = IntegerField("Servings",
                            validators=[Optional(),
                                        NumberRange(min=1, max=999)])
    category = SelectField("Category", choices=CATEGORIES, validators=[Optional()])
    submit = SubmitField("Save Recipe")
