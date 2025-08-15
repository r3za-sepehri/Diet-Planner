# core/ai_planner.py
import textwrap

def create_prompt_for_user(solution_for_day, day_name, num_meals, num_snacks, prefs):
    """
    Generates a detailed, persona-driven text prompt for an AI chat service.

    Args:
        solution_for_day (dict): Food items as keys and grams as values for a single day.
        day_name (str): The name of the day (e.g., "Monday").
        num_meals (int): The number of main meals.
        num_snacks (int): The number of snacks.
        prefs (dict): A dictionary of user preferences for the AI prompt.

    Returns:
        str: A formatted string containing the complete prompt.
    """
    day_title = day_name.replace('_', ' ').title()
    
    ingredient_list_str = "\n".join(
        [f"- {name.replace('_', ' ').title()}: {grams} g" for name, grams in solution_for_day.items()]
    )
    
    goal_str = f"- **Primary Dietary Goal:** {prefs.get('goal')}" if prefs.get('goal') and prefs.get('goal') != "General Balanced Diet" else ""
    custom_instructions = f"- **Custom Notes:** {prefs['custom_instructions']}" if prefs.get('custom_instructions') else ""
    cuisine_style = f"- **Preferred Cuisine Style:** {prefs['cuisine']}" if prefs.get('cuisine') and prefs.get('cuisine') != "Any" else ""

    cooking_method_instruction = ""
    if prefs.get('goal') == "Heart Health (Low Cholesterol)":
        cooking_method_instruction = "- **Cooking Method:** Prioritize low-fat methods like grilling, baking, steaming, or boiling. **Do not fry ingredients.**"

    user_profile_lines = [
        goal_str, 
        cuisine_style, 
        f"- **Cooking Time:** Please ensure main meals take no more than {prefs.get('cook_time', 30)} minutes to prepare.", 
        cooking_method_instruction,
        custom_instructions
    ]
    user_profile_str = "\n".join(filter(None, user_profile_lines))


    prompt = f"""
    You are an expert meal planner and creative chef. Your task is to create a delicious and inspiring meal plan for a single day based on a user's specific goals and a strict list of ingredients.

    **USER PROFILE & GOALS:**
    {user_profile_str}

    ---
    **CRITICAL RULES:**
    1.  **USE ONLY THE PROVIDED INGREDIENTS:** You must use the exact ingredients and quantities from the list below for the main components of the meal.
    2.  **YOU MAY ADD FLAVOR:** You are allowed to use common, negligible-calorie ingredients like salt, pepper, herbs, spices, and zero-calorie liquids like water or vinegar. Do not add any other ingredients that have calories (like oil, sugar, or flour) unless they are on the list.
    3.  **ADHERE TO THE GOAL:** The names of the meals and the recipe descriptions should be encouraging and align with the user's goal (e.g., "High-Protein Power Lunch," "Light & Energizing Snack").
    4.  **FORMAT THE OUTPUT:** Use Markdown for clarity with headings for each meal (`### Meal Name`).

    ---
    **DAY TO PLAN: {day_title}**

    **INGREDIENT LIST (USE ONLY THESE FOR CALORIE-CONTAINING COMPONENTS):**
    {ingredient_list_str}

    ---
    **PLAN STRUCTURE:**
    - Create a plan with {num_meals} main meal(s) and {num_snacks} snack(s).
    - For each meal/snack, provide:
        1. An appetizing name.
        2. Simple, step-by-step preparation instructions.
        3. A brief, encouraging description that ties into the user's goal.

    Now, please generate the complete meal plan for {day_title}.
    """
    
    return textwrap.dedent(prompt).strip()