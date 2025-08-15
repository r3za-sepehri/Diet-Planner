import streamlit as st
from . import ui_utils

def display_profile_page(INTAKE_REQS, requirements_calculator):
    """Renders the UI for Step 1: User Profile."""
    st.header("Step 1: Your Profile", divider='rainbow')
    st.markdown("Enter your personal data to calculate your unique nutritional needs.")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age (years)", min_value=3, max_value=120, value=30)
            weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=250.0, value=70.0, step=0.5)
            height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=175.0, step=0.5)
            gender = st.radio("Gender", ["Female", "Male"], horizontal=True, key="gender_radio")

        with col2:
            num_meals = st.number_input("Meals per day", min_value=1, max_value=10, value=3)
            num_snacks = st.number_input("Snacks per day", min_value=0, max_value=10, value=2)
            activity = st.selectbox(
                "Physical Activity Level",
                ["Sedentary", "Low Active", "Active", "Very Active"],
                index=1,
                help=(
                    "**Sedentary:** Typical daily living activities (e.g., household tasks, walking to the bus).\n\n"
                    "**Low Active:** Typical daily living activities PLUS 30-60 minutes of daily moderate activity (e.g., walking at 5-7 km/h).\n\n"
                    "**Active:** Typical daily living activities PLUS at least 60 minutes of daily moderate activity.\n\n"
                    "**Very Active:** Typical daily living activities PLUS at least 60 minutes of daily moderate activity PLUS an additional 60 minutes of vigorous activity or 120 minutes of moderate activity."
                )
            )
            if st.session_state.get('gender_radio') == "Female":
                preg_lact_status = st.selectbox(
                    "Pregnancy/Lactation Status",
                    ["Not Pregnant/Lactating", "Pregnant", "Postpartum (Lactating)"]
                )
                if preg_lact_status == "Pregnant":
                    trimester = st.selectbox("Trimester", [1, 2, 3], index=1)
                elif preg_lact_status == "Postpartum (Lactating)":
                    postpartum_period = st.selectbox("Postpartum Period", ["0-6 Months", "7+ Months"])

        submitted = st.form_submit_button("Save Profile & Calculate Needs", type="primary", use_container_width=True)

    if submitted:
        try:
            is_preg = (gender == "Female" and 'preg_lact_status' in locals() and preg_lact_status == "Pregnant")
            is_lact = (gender == "Female" and 'preg_lact_status' in locals() and preg_lact_status == "Postpartum (Lactating)")
            
            personalized_reqs = requirements_calculator.calculate_full_nutrient_requirements(
                base_intake_df=INTAKE_REQS, gender=gender.lower(), age=age, weight_kg=weight_kg,
                height_m=height_cm / 100.0, activity=ui_utils._unformat_name(activity), is_pregnant=is_preg,
                trimester=trimester if is_preg else 0, is_lactating=is_lact,
                postpartum_period={"0-6 Months": 3, "7+ Months": 9}.get(postpartum_period if is_lact else "", 0)
            )
            
            st.session_state.nutrient_reqs = personalized_reqs
            st.session_state.user_data = {'num_meals': num_meals, 'num_snacks': num_snacks, 'weight_kg': weight_kg}
            st.session_state.plan_results = None 
            st.session_state.dietary_goal_selected = None
            st.session_state.optimization_strategy_selected = None
            st.session_state.include_list = []
            st.session_state.exclude_list = []
            st.session_state.custom_foods = []
            st.session_state.custom_prices = {}

            st.success("Your profile has been saved! Proceeding to the next step...")
            
            ui_utils.go_to_page("Step 2: Select Plan Goals")
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred during calculation: {e}")