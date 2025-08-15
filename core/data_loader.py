# core/data_loader.py
import pandas as pd
import os

# Define the path to the data directory relative to this file's location
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def load_coffee_data():
    """Loads and cleans the coffee nutritional data."""
    coffee_file_path = os.path.join(DATA_DIR, 'coffee_nutritional_value.csv')
    if not os.path.exists(coffee_file_path):
        return None # Return None if the file doesn't exist
    
    coffee_df = pd.read_csv(coffee_file_path)
    coffee_df.columns = [c.strip().lower() for c in coffee_df.columns]
    coffee_df['coffee_type'] = coffee_df['coffee_type'].str.strip()
    coffee_df = coffee_df.set_index('coffee_type')
    return coffee_df

def load_and_clean_data():
    """
    Loads all required data from CSV files, cleans it, and aligns it.
    ... (rest of the docstring is unchanged) ...
    Returns:
        A tuple containing five items:
        - nutrition_df (pd.DataFrame): Nutritional values per gram.
        - prices_series (pd.Series): Price per gram.
        - intake_df (pd.DataFrame): Lower and upper nutrient bounds.
        - food_group_map (dict): A mapping of food_item -> food_group.
        - coffee_df (pd.DataFrame or None): Nutritional values for coffee types.
    """
    try:
        # --- Load Data from CSV Files ---
        nutrition_df = pd.read_csv(os.path.join(DATA_DIR, 'nutritive_value.csv'))
        prices_df = pd.read_csv(os.path.join(DATA_DIR, 'prices.csv'))
        intake_df = pd.read_csv(os.path.join(DATA_DIR, 'recommended_daily_intake.csv'))
        coffee_df = load_coffee_data() # Load coffee data
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Required data file not found: {e}. Ensure the 'data' directory is correct.")

    # --- Clean and Process Nutrition Data ---
    nutrition_df['food_item'] = nutrition_df['food_item'].str.strip().str.lower()
    food_group_map = nutrition_df.set_index('food_item')['food_group'].to_dict()
    nutrition_df = nutrition_df.set_index('food_item').drop(columns=['food_group'])
    # Ensure all nutrient columns are numeric, filling any parsing errors with 0
    for col in nutrition_df.columns:
        nutrition_df[col] = pd.to_numeric(nutrition_df[col], errors='coerce')
    nutrition_df.fillna(0, inplace=True)

    # --- Clean and Process Price Data ---
    prices_df['food_item'] = prices_df['food_item'].str.strip().str.lower()
    prices_series = prices_df.dropna().set_index('food_item')['price_per_gram']

    # --- Clean and Process Intake Data ---
    intake_df['item'] = intake_df['item'].str.strip().str.lower()
    intake_df = intake_df.set_index('item')
    intake_df['lower_bound'] = pd.to_numeric(intake_df['lower_bound'], errors='coerce')
    intake_df['upper_bound'] = pd.to_numeric(intake_df['upper_bound'], errors='coerce')

    # --- Align Data: Only use foods present in both nutrition and price tables ---
    common_foods = sorted(list(set(nutrition_df.index) & set(prices_series.index)))
    nutrition_df = nutrition_df.loc[common_foods]
    prices_series = prices_series.loc[common_foods]
    food_group_map = {food: group for food, group in food_group_map.items() if food in common_foods}

    # --- Align Nutrients: Only use nutrients with defined intake bounds, plus essential macros ---
    nutrients_with_bounds = sorted(list(set(nutrition_df.columns) & set(intake_df.index)))
    required_macro_cols = ['calorie', 'protein', 'total_fat', 'carbohydrate']
    final_nutrition_cols = sorted(list(set(nutrients_with_bounds) | set(required_macro_cols)))

    nutrition_df = nutrition_df[final_nutrition_cols]
    intake_df = intake_df.loc[nutrients_with_bounds]

    return nutrition_df, prices_series, intake_df, food_group_map, coffee_df