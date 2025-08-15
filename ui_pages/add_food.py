import streamlit as st
import pandas as pd
from . import ui_utils

def display_add_food_page(UNIQUE_GROUPS, NUTRITION_DATA, ALL_FOODS):
    st.header("Add a Custom Food", divider='rainbow')
    st.markdown("""
    Use this page to add new foods to the program for this session. The foods you add will become available in the 'Create Plan' step.
    
    **Instructions:**
    1. Find your food item in the [**USDA Nutritive Value of Foods PDF**](https://www.ars.usda.gov/ARSUserFiles/80400535/pdf/hg72.pdf).
    2. In the form below, enter the **serving size** (e.g., "1 cup") and its **weight in grams** exactly as listed in the book.
    3. Fill in the nutrient values for that specific serving. The app will automatically calculate the per-gram values for the optimizer.
    """)

    nutrient_columns = ['calorie', 'protein', 'total_fat', 'saturated_fat', 'carbohydrate', 'fiber', 'calcium', 'iron', 'potassium', 'sodium', 'vitamin_a', 'thiamin', 'riboflavin', 'niacin', 'ascorbic_acid']
    with st.form("add_food_form"):
        st.subheader("Food Identification")
        food_name = st.text_input("Food Name (e.g., Quinoa, cooked)")
        food_group = st.selectbox("Food Group", options=UNIQUE_GROUPS)
        st.subheader("Serving and Price Information")
        col1, col2 = st.columns(2)
        serving_desc = col1.text_input("Household Serving (e.g., 1 cup)", "1 cup")
        serving_weight_g = col2.number_input("Weight of this Serving (g)", min_value=1.0, value=150.0)
        pkg_weight_g = col1.number_input("Package Weight (g)", min_value=1.0, value=500.0)
        pkg_price = col2.number_input("Package Price", min_value=0.01, value=5.00)
        st.subheader("Nutrient Values for the Serving Size Above")
        cols = st.columns(4)
        nutrient_inputs = {nutrient: cols[i % 4].number_input(f"{ui_utils._format_name(nutrient)} (for serving)", min_value=0.0, format="%.2f") for i, nutrient in enumerate(nutrient_columns)}
        submitted = st.form_submit_button("Add Custom Food", use_container_width=True)
    if submitted:
        if not food_name or not food_group or serving_weight_g <= 0:
            st.error("Please fill in the Food Name, Group, and a valid Serving Weight.")
        else:
            internal_name = ui_utils._unformat_name(food_name)
            if any(f['name'] == internal_name for f in st.session_state.custom_foods) or internal_name in ALL_FOODS:
                st.error(f"The food '{food_name}' already exists.")
            else:
                nutrients_per_gram = {nutrient: value / serving_weight_g for nutrient, value in nutrient_inputs.items()}
                for col in NUTRITION_DATA.columns:
                    if col not in nutrients_per_gram: nutrients_per_gram[col] = 0
                new_food = {'name': internal_name, 'display_name': food_name, 'group': food_group, 'price_per_gram': pkg_price / pkg_weight_g, 'nutrients': nutrients_per_gram}
                st.session_state.custom_foods.append(new_food)
                st.success(f"Successfully added '{food_name}' to your custom food list!")
    if st.session_state.custom_foods:
        st.subheader("Custom Foods Added in this Session")
        display_data = [{"Food Name": f['display_name'], "Food Group": ui_utils._format_name(f['group']), "Price per 100g": f"{(f['price_per_gram'] * 100):.2f}"} for f in st.session_state.custom_foods]
        st.dataframe(display_data, use_container_width=True)
        food_to_remove = st.selectbox("Select a food to remove", [""] + [f['display_name'] for f in st.session_state.custom_foods])
        if st.button("Remove Selected Food"):
            st.session_state.custom_foods = [f for f in st.session_state.custom_foods if f['display_name'] != food_to_remove]
            st.rerun()