"""
Seed the database with 100 sample recipes.
Run with: python seed_recipes.py
"""
from app import create_app, db
from app.models import User, Recipe

RECIPES_DATA = [
    {
        "title": "Classic Margherita Pizza",
        "description": "Traditional Italian pizza with fresh mozzarella, basil, and tomato sauce.",
        "ingredients": "2 cups flour\n1 tbsp yeast\n1 cup water\n500g mozzarella\n200g tomato sauce\n20 fresh basil leaves\nSalt and olive oil",
        "instructions": "1. Mix flour, yeast, and water to form dough.\n2. Let rise for 1 hour.\n3. Spread tomato sauce on dough.\n4. Add mozzarella and basil.\n5. Bake at 220°C for 15 minutes.",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 2,
        "category": "Dinner"
    },
    {
        "title": "Spaghetti Carbonara",
        "description": "Creamy Roman pasta with bacon, eggs, and parmesan cheese.",
        "ingredients": "400g spaghetti\n200g pancetta\n4 eggs\n100g parmesan\nBlack pepper\nSalt",
        "instructions": "1. Cook spaghetti in salted boiling water.\n2. Dice and fry pancetta.\n3. Mix eggs with grated parmesan.\n4. Toss hot pasta with pancetta and egg mixture.\n5. Season with pepper.",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "category": "Dinner"
    },
    {
        "title": "Chicken Tikka Masala",
        "description": "Spiced Indian chicken in creamy tomato sauce, served with rice.",
        "ingredients": "800g chicken breast\n200g yogurt\n3 tbsp tikka paste\n400ml coconut milk\n400g canned tomatoes\n2 onions\n3 cloves garlic\nCilantro\nRice",
        "instructions": "1. Marinate chicken in yogurt and tikka paste for 2 hours.\n2. Cook chicken in a pan until golden.\n3. Sauté onions and garlic.\n4. Add tomatoes and coconut milk.\n5. Simmer for 20 minutes. Serve with rice and cilantro.",
        "prep_time": 15,
        "cook_time": 35,
        "servings": 4,
        "category": "Dinner"
    },
    {
        "title": "Chocolate Chip Cookies",
        "description": "Classic chewy cookies loaded with chocolate chips.",
        "ingredients": "225g butter\n200g brown sugar\n100g white sugar\n2 eggs\n2 tsp vanilla\n280g flour\n1 tsp baking soda\n1 tsp salt\n340g chocolate chips",
        "instructions": "1. Cream butter and sugars.\n2. Beat in eggs and vanilla.\n3. Mix flour, baking soda, and salt.\n4. Combine wet and dry ingredients.\n5. Fold in chocolate chips.\n6. Bake at 190°C for 12 minutes.",
        "prep_time": 15,
        "cook_time": 12,
        "servings": 24,
        "category": "Dessert"
    },
    {
        "title": "Caesar Salad",
        "description": "Crisp romaine lettuce with parmesan, croutons, and tangy Caesar dressing.",
        "ingredients": "1 head romaine lettuce\n100g parmesan\n200g croutons\n3 tbsp mayonnaise\n2 cloves garlic\n1 tbsp lemon juice\n1 tsp Worcestershire sauce\nAnchovies (optional)",
        "instructions": "1. Whisk mayonnaise, garlic, lemon juice, and Worcestershire.\n2. Tear romaine lettuce.\n3. Toss with dressing.\n4. Top with parmesan and croutons.",
        "prep_time": 10,
        "cook_time": 0,
        "servings": 4,
        "category": "Salad"
    },
    {
        "title": "Beef Tacos",
        "description": "Seasoned ground beef in soft tortillas with fresh toppings.",
        "ingredients": "500g ground beef\n2 tbsp taco seasoning\n8 flour tortillas\n100g cheddar\n100g sour cream\n2 tomatoes\n1 onion\nLettuce\nSalsa",
        "instructions": "1. Brown ground beef in a skillet.\n2. Add taco seasoning and water, simmer 10 minutes.\n3. Warm tortillas.\n4. Fill with beef, cheese, and toppings.\n5. Serve with salsa and sour cream.",
        "prep_time": 15,
        "cook_time": 15,
        "servings": 4,
        "category": "Dinner"
    },
    {
        "title": "Greek Salad",
        "description": "Fresh Mediterranean salad with feta cheese, olives, and tomatoes.",
        "ingredients": "4 tomatoes\n1 cucumber\n200g feta cheese\n100g black olives\n1 red onion\n3 tbsp olive oil\n1 tbsp balsamic vinegar\nOregano",
        "instructions": "1. Chop tomatoes and cucumber.\n2. Dice feta cheese.\n3. Combine vegetables in a bowl.\n4. Whisk olive oil and vinegar.\n5. Toss salad with dressing and oregano.",
        "prep_time": 15,
        "cook_time": 0,
        "servings": 4,
        "category": "Salad"
    },
    {
        "title": "Pad Thai",
        "description": "Stir-fried rice noodles with shrimp, tofu, and peanuts.",
        "ingredients": "300g rice noodles\n250g shrimp\n200g tofu\n100g roasted peanuts\n3 eggs\n2 cloves garlic\n3 tbsp tamarind paste\n2 tbsp fish sauce\n1 tbsp lime juice\nBean sprouts",
        "instructions": "1. Soak rice noodles in warm water.\n2. Stir-fry shrimp and tofu.\n3. Add noodles and sauce.\n4. Push to the side, scramble eggs.\n5. Toss together and serve with peanuts and bean sprouts.",
        "prep_time": 20,
        "cook_time": 10,
        "servings": 4,
        "category": "Dinner"
    },
    {
        "title": "Pancakes",
        "description": "Fluffy buttermilk pancakes perfect for breakfast.",
        "ingredients": "200g flour\n2 tbsp sugar\n2 tsp baking powder\n1 tsp salt\n250ml buttermilk\n2 eggs\n2 tbsp melted butter\nMaple syrup",
        "instructions": "1. Mix flour, sugar, baking powder, and salt.\n2. Whisk buttermilk, eggs, and butter.\n3. Combine wet and dry ingredients.\n4. Cook on griddle until golden on both sides.\n5. Serve with maple syrup.",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "category": "Breakfast"
    },
    {
        "title": "Tomato Soup",
        "description": "Creamy tomato soup with fresh basil and croutons.",
        "ingredients": "800g canned tomatoes\n1 onion\n3 cloves garlic\n200ml heavy cream\n500ml vegetable broth\n20 fresh basil leaves\nOlive oil\nSalt and pepper",
        "instructions": "1. Sauté onion and garlic in olive oil.\n2. Add tomatoes and broth, simmer 20 minutes.\n3. Blend until smooth.\n4. Stir in cream and basil.\n5. Season with salt and pepper.",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "category": "Soup"
    },
]

RECIPE_TEMPLATES = [
    {
        "title": "Pasta {style}",
        "description": "{style} pasta with fresh ingredients and authentic flavours.",
        "ingredients": "400g pasta\n{ing1}\n{ing2}\n{ing3}\nGarlic\nOlive oil\nSalt and pepper",
        "instructions": "1. Cook pasta in salted water.\n2. Prepare sauce with {ing1} and {ing2}.\n3. Toss pasta with sauce.\n4. Garnish with {ing3}.\n5. Serve hot.",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 4,
        "category": "Dinner"
    },
    {
        "title": "Grilled {protein}",
        "description": "Tender {protein} with herbs and seasonal vegetables.",
        "ingredients": "{protein}\n{veg1}\n{veg2}\nLemon\nOlive oil\nRosemary\nThyme\nGarlic",
        "instructions": "1. Season {protein} with herbs.\n2. Grill for {time} minutes each side.\n3. Grill vegetables alongside.\n4. Serve with lemon wedges.",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "category": "Dinner"
    },
    {
        "title": "{cuisine} Bowl",
        "description": "Nourishing {cuisine} bowl with grains, protein, and fresh vegetables.",
        "ingredients": "200g {grain}\n{protein}\n{veg1}\n{veg2}\n{sauce}\nLime juice\nCilantro",
        "instructions": "1. Cook {grain}.\n2. Prepare protein.\n3. Chop vegetables.\n4. Arrange in bowl.\n5. Drizzle with {sauce}.",
        "prep_time": 20,
        "cook_time": 25,
        "servings": 2,
        "category": "Lunch"
    },
]

STYLES = ["Alfredo", "Carbonara", "Marinara", "Pesto", "Aglio e Olio"]
PROTEINS = ["Salmon", "Chicken Breast", "Steak", "Pork Chops", "Lamb"]
VEGGIES = [
    ("Broccoli", "Asparagus"),
    ("Bell Peppers", "Zucchini"),
    ("Green Beans", "Carrots"),
    ("Brussels Sprouts", "Mushrooms"),
]
CUISINES = ["Mexican", "Thai", "Vietnamese", "Korean", "Indian", "Japanese", "Mediterranean"]
GRAINS = ["Rice", "Quinoa", "Couscous"]
PROTEINS_BASE = ["Chicken", "Tofu", "Chickpeas", "Tempeh"]
SAUCES = ["Tahini Dressing", "Lime Vinaigrette", "Soy Sauce", "Miso Dressing"]

def generate_recipes():
    """Generate 100 recipes with variety."""
    recipes = list(RECIPES_DATA)
    
    # Template-based recipes
    for i in range(20):
        style = STYLES[i % len(STYLES)]
        recipes.append({
            "title": f"Pasta {style} v{i//5 + 1}",
            "description": f"{style} pasta with fresh ingredients and authentic flavours.",
            "ingredients": f"400g pasta\n200g {['cream', 'tomato', 'olive oil', 'pesto', 'garlic'][i % 5]}\nGarlic\nOlive oil\nSalt and pepper",
            "instructions": "1. Cook pasta.\n2. Prepare sauce.\n3. Toss and serve.",
            "prep_time": 10 + (i % 15),
            "cook_time": 15 + (i % 15),
            "servings": 2 + (i % 4),
            "category": "Dinner"
        })
    
    for i in range(18):
        protein = PROTEINS[i % len(PROTEINS)]
        veg1, veg2 = VEGGIES[i % len(VEGGIES)]
        recipes.append({
            "title": f"Grilled {protein} v{i//5 + 1}",
            "description": f"Tender {protein} with herbs and grilled {veg1}.",
            "ingredients": f"{protein}\n{veg1}\n{veg2}\nLemon\nOlive oil\nRosemary\nThyme",
            "instructions": "1. Season protein.\n2. Grill 15-20 minutes.\n3. Serve with vegetables.",
            "prep_time": 10,
            "cook_time": 20 + (i % 10),
            "servings": 2 + (i % 4),
            "category": "Dinner"
        })
    
    for i in range(18):
        cuisine = CUISINES[i % len(CUISINES)]
        grain = GRAINS[i % len(GRAINS)]
        protein = PROTEINS_BASE[i % len(PROTEINS_BASE)]
        veg1, veg2 = VEGGIES[i % len(VEGGIES)]
        sauce = SAUCES[i % len(SAUCES)]
        recipes.append({
            "title": f"{cuisine} {grain} Bowl v{i//7 + 1}",
            "description": f"Nutritious {cuisine} bowl with {grain}, {protein}, and fresh veggies.",
            "ingredients": f"200g {grain}\n{protein}\n{veg1}\n{veg2}\n{sauce}\nLime juice\nCilantro",
            "instructions": "1. Cook grain.\n2. Prepare protein.\n3. Chop vegetables.\n4. Assemble in bowl.",
            "prep_time": 15 + (i % 10),
            "cook_time": 20 + (i % 10),
            "servings": 1 + (i % 3),
            "category": "Lunch"
        })
    
    # Desserts
    desserts = [
        ("Brownies", "Rich, fudgy chocolate brownies."),
        ("Cheesecake", "Creamy New York style cheesecake."),
        ("Tiramisu", "Italian dessert with mascarpone and espresso."),
        ("Lemon Bars", "Tangy lemon bars with shortbread crust."),
        ("Chocolate Mousse", "Light and airy chocolate mousse."),
        ("Apple Pie", "Classic apple pie with cinnamon."),
        ("Carrot Cake", "Moist carrot cake with cream cheese frosting."),
    ]
    for i, (title, desc) in enumerate(desserts):
        recipes.append({
            "title": title,
            "description": desc,
            "ingredients": f"200g {['flour', 'sugar', 'butter', 'eggs', 'apples', 'carrots'][i % 6]}\n{['chocolate', 'cream', 'lemons', 'vanilla', 'cinnamon', 'cream cheese'][i % 6]}\nSugar\nEggs\nButter",
            "instructions": "1. Prepare ingredients.\n2. Mix and bake.\n3. Cool before serving.",
            "prep_time": 20 + (i % 15),
            "cook_time": 30 + (i % 15),
            "servings": 8 + (i % 4),
            "category": "Dessert"
        })
    
    # Breakfast items
    breakfasts = [
        ("Oatmeal", "Warm, creamy steel-cut oatmeal."),
        ("French Toast", "Crispy on outside, custardy inside."),
        ("Shakshuka", "Middle Eastern eggs in tomato sauce."),
        ("Granola", "Homemade crunchy granola."),
        ("Waffles", "Golden, fluffy waffles."),
        ("Eggs Benedict", "Poached eggs with hollandaise sauce."),
        ("Bagel & Lox", "Smoked salmon with cream cheese and dill."),
    ]
    for i, (title, desc) in enumerate(breakfasts):
        recipes.append({
            "title": title,
            "description": desc,
            "ingredients": f"{['Oats', 'Bread', 'Eggs', 'Flour', 'Flour', 'Muffins', 'Bagels'][i]}\nMilk\nSugar\n{['berries', 'maple syrup', 'tomatoes', 'nuts', 'berries', 'hollandaise', 'lox'][i]}",
            "instructions": "1. Prepare base.\n2. Cook until done.\n3. Add toppings.",
            "prep_time": 10,
            "cook_time": 15 + (i % 10),
            "servings": 2 + (i % 2),
            "category": "Breakfast"
        })
    
    # Soups
    soups = [
        ("Minestrone", "Italian vegetable soup with pasta."),
        ("Butternut Squash Soup", "Creamy autumn soup."),
        ("Chicken Noodle Soup", "Classic comfort soup."),
        ("Lentil Soup", "Hearty and nutritious."),
        ("Clam Chowder", "Creamy New England clam chowder."),
        ("French Onion Soup", "Rich caramelized onion soup."),
        ("Mushroom Soup", "Earthy mushroom soup with herbs."),
    ]
    for i, (title, desc) in enumerate(soups):
        recipes.append({
            "title": title,
            "description": desc,
            "ingredients": f"{['Vegetables', 'Squash', 'Chicken', 'Lentils', 'Clams', 'Onions', 'Mushrooms'][i]}\nBroth\nOnion\nGarlic\n{['Pasta', 'Cream', 'Noodles', 'Spices', 'Potatoes', 'Cheese', 'Herbs'][i]}",
            "instructions": "1. Sauté aromatics.\n2. Add ingredients.\n3. Simmer 30 minutes.",
            "prep_time": 15,
            "cook_time": 35,
            "servings": 4 + (i % 2),
            "category": "Soup"
        })
    
    # Snacks
    snacks = [
        ("Hummus & Veggies", "Creamy chickpea hummus with fresh vegetables."),
        ("Trail Mix", "Nuts, dried fruit, and dark chocolate mix."),
        ("Guacamole & Chips", "Fresh avocado dip with tortilla chips."),
        ("Energy Balls", "No-bake oat and peanut butter bites."),
        ("Nachos", "Crispy chips with cheese and jalapeños."),
        ("Cucumber Sandwiches", "Delicate tea-time sandwiches."),
    ]
    for i, (title, desc) in enumerate(snacks):
        recipes.append({
            "title": title,
            "description": desc,
            "ingredients": f"{['Chickpeas', 'Nuts', 'Avocados', 'Oats', 'Tortilla chips', 'Cucumber'][i]}\n{['Tahini', 'Dried fruit', 'Lime', 'Peanut butter', 'Cheese', 'Cream cheese'][i]}\nSalt\nSpices",
            "instructions": "1. Prepare base ingredient.\n2. Mix and combine.\n3. Serve immediately.",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 2,
            "category": "Snack"
        })
    
    # Beverages
    beverages = [
        ("Smoothie Bowl", "Thick smoothie topped with granola and fruit."),
        ("Iced Tea", "Refreshing homemade iced tea."),
        ("Matcha Latte", "Creamy matcha green tea latte."),
        ("Mojito", "Refreshing mint and lime cocktail."),
        ("Espresso Martini", "Coffee-infused cocktail."),
        ("Kombucha", "Fermented tea beverage."),
    ]
    for i, (title, desc) in enumerate(beverages):
        recipes.append({
            "title": title,
            "description": desc,
            "ingredients": f"{['Yogurt', 'Tea', 'Matcha', 'Mint', 'Coffee', 'Tea'][i]}\n{['Berries', 'Lemon', 'Milk', 'Rum', 'Vodka', 'SCOBY'][i]}\nSugar\nWater",
            "instructions": "1. Gather ingredients.\n2. Mix and blend or brew.\n3. Serve cold.",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 1,
            "category": "Beverage"
        })
    
    return recipes[:100]

def main():
    app = create_app()
    with app.app_context():
        # Create test user if not exists
        user = User.query.filter_by(username="chef_demo").first()
        if not user:
            user = User(username="chef_demo", email="chef@demo.com")
            user.set_password("DemoPassword123")
            db.session.add(user)
            db.session.commit()
            print(f"✓ Created user: {user.username}")
        else:
            print(f"✓ User already exists: {user.username}")
        
        # Clear existing recipes (optional)
        existing = Recipe.query.filter_by(user_id=user.id).count()
        if existing > 0:
            print(f"ℹ User already has {existing} recipes. Skipping...")
            return
        
        # Generate and insert recipes
        recipes_data = generate_recipes()
        for i, recipe_data in enumerate(recipes_data):
            recipe = Recipe(
                user_id=user.id,
                **recipe_data
            )
            db.session.add(recipe)
            if (i + 1) % 20 == 0:
                db.session.commit()
                print(f"✓ Added {i + 1} recipes...")
        
        db.session.commit()
        print(f"✓ Successfully added {len(recipes_data)} recipes to the database!")
        print(f"✓ All recipes authored by: {user.username}")

if __name__ == "__main__":
    main()
