# core/requirements_calculator.py
import pandas as pd

def get_pa_coefficient(gender, age, activity_level):
    """
    Returns the Physical Activity (PA) coefficient based on gender, age, and activity level.
    These values are based on the Dietary Reference Intakes (DRI) from the Institute of Medicine.
    """
    pa_coeffs = {
        "male": {
            "3-18": {"sedentary": 1.0, "low_active": 1.13, "active": 1.26, "very_active": 1.42},
            "19+": {"sedentary": 1.0, "low_active": 1.11, "active": 1.25, "very_active": 1.48}
        },
        "female": {
            "3-18": {"sedentary": 1.0, "low_active": 1.16, "active": 1.31, "very_active": 1.56},
            "19+": {"sedentary": 1.0, "low_active": 1.12, "active": 1.27, "very_active": 1.45}
        }
    }
    age_group = "3-18" if 3 <= age <= 18 else "19+"
    return pa_coeffs[gender][age_group].get(activity_level, 1.0)

def calculate_requirements_logic(gender, age, weight_kg, height_m, activity,
                               is_pregnant=False, trimester=0,
                               is_lactating=False, postpartum_period=0):
    """
    Calculates Estimated Energy Requirement (EER) and basic protein needs.
    Formulas are based on the Dietary Reference Intakes (DRI) from the Institute of Medicine.
    """
    pa = get_pa_coefficient(gender, age, activity)
    eer = 0
    if gender == 'male':
        if 3 <= age <= 8:
            eer = 88.5 - (61.9 * age) + pa * ((26.7 * weight_kg) + (903 * height_m)) + 20
        elif 9 <= age <= 18:
            eer = 88.5 - (61.9 * age) + pa * ((26.7 * weight_kg) + (903 * height_m)) + 25
        else: # 19+
            eer = 662 - (9.53 * age) + pa * ((15.91 * weight_kg) + (539.6 * height_m))
    else:  # female
        if 3 <= age <= 8:
            eer = 135.3 - (30.8 * age) + pa * ((10.0 * weight_kg) + (934 * height_m)) + 20
        elif 9 <= age <= 18:
            eer = 135.3 - (30.8 * age) + pa * ((10.0 * weight_kg) + (934 * height_m)) + 25
        else: # 19+
            eer = 354 - (6.91 * age) + pa * ((9.36 * weight_kg) + (726 * height_m))
        
        if is_pregnant:
            if trimester == 2: eer += 340
            elif trimester == 3: eer += 452
        
        if is_lactating:
            if 0 <= postpartum_period <= 6: eer += (500 - 170) # 500 kcal total, 170 from body stores
            elif postpartum_period > 6: eer += 400

    protein_req = weight_kg * 0.8
    return eer, protein_req

def calculate_full_nutrient_requirements(base_intake_df, gender, age, weight_kg, height_m, activity,
                                         is_pregnant=False, trimester=0,
                                         is_lactating=False, postpartum_period=0):
    """
    Takes the base intake DataFrame and personalizes it with calculated EER and protein.
    """
    eer, protein_req = calculate_requirements_logic(
        gender=gender, age=age, weight_kg=weight_kg, height_m=height_m,
        activity=activity, is_pregnant=is_pregnant, trimester=trimester,
        is_lactating=is_lactating, postpartum_period=postpartum_period
    )
    
    personalized_reqs = base_intake_df.copy()
    
    if 'calorie' in personalized_reqs.index:
        personalized_reqs.loc['calorie', 'lower_bound'] = eer
        
    if 'protein' in personalized_reqs.index:
        personalized_reqs.loc['protein', 'lower_bound'] = protein_req
        
    return personalized_reqs

def apply_dietary_goal_adjustments(req_df, goal, weight_kg, boosted_nutrients=None):
    """
    Adjusts the nutrient requirements DataFrame based on a specific dietary goal.
    """
    adjusted_reqs = req_df.copy()
    if 'calorie' not in adjusted_reqs.index or 'protein' not in adjusted_reqs.index:
        # Cannot perform adjustments if key metrics are missing
        return adjusted_reqs
        
    calories = adjusted_reqs.loc['calorie', 'lower_bound']

    if goal == "Weight Loss":
        adjusted_reqs.loc['calorie', 'lower_bound'] = max(1200, calories - 500)
        adjusted_reqs.loc['protein', 'lower_bound'] *= 1.2
    elif goal == "Weight Gain / Muscle Building":
        adjusted_reqs.loc['calorie', 'lower_bound'] += 500
        adjusted_reqs.loc['protein', 'lower_bound'] = max(adjusted_reqs.loc['protein', 'lower_bound'], weight_kg * 1.6)
    elif goal == "Heart Health (Low Cholesterol)":
        if 'fiber' in adjusted_reqs.index:
            adjusted_reqs.loc['fiber', 'lower_bound'] = max(adjusted_reqs.loc['fiber', 'lower_bound'], 35)
        if 'saturated_fat' in adjusted_reqs.index:
            # Set saturated fat limit to 10% of total calories (in grams)
            adjusted_reqs.loc['saturated_fat', 'upper_bound'] = (calories * 0.1) / 9
    elif goal == "Diabetes Management":
        if 'fiber' in adjusted_reqs.index:
            adjusted_reqs.loc['fiber', 'lower_bound'] = max(adjusted_reqs.loc['fiber', 'lower_bound'], 40)
    elif goal == "Athletic Performance":
        adjusted_reqs.loc['protein', 'lower_bound'] = max(adjusted_reqs.loc['protein', 'lower_bound'], weight_kg * 1.4)
    elif goal == "Cold / Immune Boost":
        if 'vitamin_c' in adjusted_reqs.index:
            adjusted_reqs.loc['vitamin_c', 'lower_bound'] *= 3.0
    elif goal == "Nutrient Booster" and boosted_nutrients:
        for nutrient in boosted_nutrients:
            internal_name = _unformat_name(nutrient)
            if internal_name in adjusted_reqs.index:
                # Apply a 50% boost to the lower bound
                adjusted_reqs.loc[internal_name, 'lower_bound'] *= 1.5

    return adjusted_reqs

def _unformat_name(formatted_name):
    return formatted_name.replace(' ', '_').lower()