# core/optimizer.py
import itertools
import pandas as pd
from pulp import LpProblem, LpMinimize, LpMaximize, LpVariable, lpSum, LpStatus, getSolver

# =============================================================================
# --- GLOBAL CONSTRAINT PARAMETERS ---
# =============================================================================

MUTUALLY_EXCLUSIVE_GROUPS = [
    ['low_fat_milk', 'high_fat_milk'],
    ['bread', 'whole_bread'],
    ['canolla_oil', 'corn_oil', 'sunseed_oil', 'olive_oil']
]

BALANCED_ENERGY_TOLERANCE = 0.20 # +/- 20%
MAX_ITEMS_PER_GROUP_FOR_BALANCE = 5

FOOD_GROUP_CALORIE_DIST = {
    'starchy_staples': 0.50,
    'fruits': 0.07,
    'vegetables': 0.05,
    'oils_and_fats': 0.12,
    'animal_source_foods': 0.13,
    'legumes_nuts_and_seeds': 0.13
}
MACRO_CALORIE_DIST = {
    'carbohydrate': {'min': 0.45, 'max': 0.65, 'kcal_per_g': 4},
    'total_fat':    {'min': 0.20, 'max': 0.35, 'kcal_per_g': 9},
    'protein':      {'min': 0.10, 'max': 0.35, 'kcal_per_g': 4}
}
BIG_M_GRAMS = 4000
BIG_M_CALORIES = 10000

def _add_common_constraints(prob, food_vars, food_is_selected, nutrition_df, intake_df, food_group_map,
                           foods, foods_to_include, daily_diversity_target, days, nutrient_mode,
                           min_daily_group_variety, weekly_max_occurrences, balance_energy_rule_active,
                           apply_repetition_cap_to_staples):
    """Helper function to add constraints common to the model."""
    food_groups = sorted(list(set(food_group_map.values())))
    var_keys = [(f, d) for f in foods for d in days]

    for d in days:
        total_calories_day = lpSum(nutrition_df.loc[f, 'calorie'] * food_vars[(f, d)] for f in foods)
        prob += lpSum(food_is_selected[(f, d)] for f in foods) >= daily_diversity_target, f"DailyDiversity_{d}"
        
        for group, percentage in FOOD_GROUP_CALORIE_DIST.items():
            foods_in_group = [f for f in foods if food_group_map.get(f) == group]
            if foods_in_group:
                group_calories = lpSum(nutrition_df.loc[f, 'calorie'] * food_vars[(f, d)] for f in foods_in_group)
                prob += group_calories == percentage * total_calories_day, f"Calorie_Dist_{group}_{d}"
        
        for macro, values in MACRO_CALORIE_DIST.items():
            if macro in nutrition_df.columns:
                macro_calories = values['kcal_per_g'] * lpSum(nutrition_df.loc[f, macro] * food_vars[(f, d)] for f in foods)
                prob += macro_calories >= values['min'] * total_calories_day, f"Macro_Min_{macro}_{d}"
                prob += macro_calories <= values['max'] * total_calories_day, f"Macro_Max_{macro}_{d}"
        
        for f in foods:
            prob += food_vars[(f, d)] <= BIG_M_GRAMS * food_is_selected[(f, d)], f"Link_{f}_{d}"

        for group, min_items in min_daily_group_variety.items():
            foods_in_group = [f for f in foods if food_group_map.get(f) == group]
            if foods_in_group:
                prob += lpSum(food_is_selected[(f, d)] for f in foods_in_group) >= min_items, f"Min_Variety_{group}_{d}"
        
        if balance_energy_rule_active:
            for group, min_items in min_daily_group_variety.items():
                if min_items > 1:
                    foods_in_group = [f for f in foods if food_group_map.get(f) == group]
                    if not foods_in_group: continue

                    total_group_calories = lpSum(nutrition_df.loc[f, 'calorie'] * food_vars[(f, d)] for f in foods_in_group)
                    
                    num_items_in_group_is_k = LpVariable.dicts(f"NumItemsInGroupIsK_{group}_{d}", range(min_items, MAX_ITEMS_PER_GROUP_FOR_BALANCE + 1), cat='Binary')
                    prob += lpSum(num_items_in_group_is_k) == 1, f"ExactlyOneKIsChosen_{group}_{d}"
                    prob += lpSum(k * num_items_in_group_is_k[k] for k in range(min_items, MAX_ITEMS_PER_GROUP_FOR_BALANCE + 1)) == lpSum(food_is_selected[(f, d)] for f in foods_in_group), f"LinkNumItemsToK_{group}_{d}"

                    for f in foods_in_group:
                        food_calories = nutrition_df.loc[f, 'calorie'] * food_vars[(f, d)]
                        
                        for k in range(min_items, MAX_ITEMS_PER_GROUP_FOR_BALANCE + 1):
                            avg_calories = total_group_calories / k
                            
                            prob += food_calories - (1 + BALANCED_ENERGY_TOLERANCE) * avg_calories <= BIG_M_CALORIES * (2 - food_is_selected[(f, d)] - num_items_in_group_is_k[k]), f"Balance_Upper_{f}_{k}_{d}"
                            prob += food_calories - (1 - BALANCED_ENERGY_TOLERANCE) * avg_calories >= -BIG_M_CALORIES * (2 - food_is_selected[(f, d)] - num_items_in_group_is_k[k]), f"Balance_Lower_{f}_{k}_{d}"


    for food in foods_to_include:
        if food in foods:
            prob += lpSum(food_is_selected[(food, d)] for d in days) >= 1, f"Force_Include_{food}_Weekly"

    nutrients_to_constrain = [n for n in intake_df.index if n in nutrition_df.columns]
    if nutrient_mode == 'daily':
        for nutrient in nutrients_to_constrain:
            for d in days:
                lower_bound, upper_bound = intake_df.loc[nutrient, 'lower_bound'], intake_df.loc[nutrient, 'upper_bound']
                total_nutrient_daily = lpSum(nutrition_df.loc[f, nutrient] * food_vars[(f, d)] for f in foods)
                if not pd.isna(lower_bound): prob += total_nutrient_daily >= lower_bound, f"Daily_Min_{nutrient}_{d}"
                if not pd.isna(upper_bound): prob += total_nutrient_daily <= upper_bound, f"Daily_Max_{nutrient}_{d}"
    
    if len(days) > 1:
        staple_foods = ['bread', 'whole_bread', 'potato', 'rice', 'spaghetti', 'canolla_oil', 'corn_oil', 'sunseed_oil', 'olive_oil', 'butter', 'low_fat_milk', 'high_fat_milk', 'yogurt', 'onion']
        
        foods_for_repetition_cap = []
        if apply_repetition_cap_to_staples:
            foods_for_repetition_cap = foods
        else:
            foods_for_repetition_cap = [f for f in foods if f not in staple_foods]
        
        for food in foods_for_repetition_cap:
            prob += lpSum(food_is_selected[(food, d)] for d in days) <= weekly_max_occurrences, f"Weekly_Max_Occurrences_{food}"

    weekly_food_is_used = LpVariable.dicts("WeeklyFoodUsed", foods, cat='Binary')
    for f in foods:
        for d in days:
            prob += weekly_food_is_used[f] >= food_is_selected[(f, d)], f"Link_Weekly_Daily_{f}_{d}"

    for group in MUTUALLY_EXCLUSIVE_GROUPS:
        foods_in_group = [f for f in group if f in foods]
        if foods_in_group:
            prob += lpSum(weekly_food_is_used[f] for f in foods_in_group) <= 1, f"Exclusive_Group_{'_'.join(foods_in_group)}"


def create_and_solve_model(nutrition_df, prices_series, intake_df, food_group_map,
                           foods_to_exclude, foods_to_include, daily_diversity_target,
                           days_of_week, nutrient_mode, variety_level, *, solver_name=None):
    """Builds and solves the weekly MILP model with cost minimization, adjusted by a variety level."""
    
    if variety_level == 1:
        min_daily_group_variety = {'fruits': 1, 'vegetables': 1, 'animal_source_foods': 1, 'starchy_staples': 1, 'legumes_nuts_and_seeds': 1}
        weekly_max_occurrences = 4
        balance_energy_rule_active = False
        apply_repetition_cap_to_staples = False
    elif variety_level == 2:
        min_daily_group_variety = {'fruits': 2, 'vegetables': 2, 'animal_source_foods': 1, 'starchy_staples': 1, 'legumes_nuts_and_seeds': 1}
        weekly_max_occurrences = 4
        balance_energy_rule_active = True
        apply_repetition_cap_to_staples = False
    elif variety_level == 3:
        min_daily_group_variety = {'fruits': 2, 'vegetables': 3, 'animal_source_foods': 1, 'starchy_staples': 2, 'legumes_nuts_and_seeds': 1}
        weekly_max_occurrences = 3
        balance_energy_rule_active = True
        apply_repetition_cap_to_staples = False 
    elif variety_level == 4:
        min_daily_group_variety = {'fruits': 2, 'vegetables': 3, 'animal_source_foods': 2, 'starchy_staples': 2, 'legumes_nuts_and_seeds': 1}
        weekly_max_occurrences = 2
        balance_energy_rule_active = True
        apply_repetition_cap_to_staples = False 
    else: # Level 5
        min_daily_group_variety = {'fruits': 3, 'vegetables': 3, 'animal_source_foods': 3, 'starchy_staples': 2, 'legumes_nuts_and_seeds': 2}
        weekly_max_occurrences = 2
        balance_energy_rule_active = True
        apply_repetition_cap_to_staples = False 

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    foods = [f for f in nutrition_df.index.tolist() if f not in foods_to_exclude]
    prob = LpProblem("Unified_Diet_Optimization", LpMinimize)
    var_keys = [(f, d) for f in foods for d in days]
    food_vars = LpVariable.dicts("FoodGrams", var_keys, lowBound=0, cat='Continuous')
    food_is_selected = LpVariable.dicts("FoodSelected", var_keys, cat='Binary')

    prob += lpSum([prices_series.get(f, 999) * food_vars[(f, d)] for f, d in var_keys]), "Total_Weekly_Cost"

    _add_common_constraints(prob, food_vars, food_is_selected, nutrition_df, intake_df, food_group_map,
                           foods, foods_to_include, daily_diversity_target, days, nutrient_mode,
                           min_daily_group_variety, weekly_max_occurrences, balance_energy_rule_active,
                           apply_repetition_cap_to_staples)
    
    prob.solve(solver_name)
    return prob, food_vars, days