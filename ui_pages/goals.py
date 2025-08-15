import streamlit as st
from . import ui_utils

def display_select_plan_goals_page():
    """Renders the UI for Step 2: Selecting Plan Goals."""
    st.header("Step 2: Select Plan Goals", divider='rainbow')

    if st.session_state.nutrient_reqs is None:
        st.warning("Please complete and save your profile in Step 1 before proceeding.")
        return

    st.subheader("Choose Your Dietary Goal")
    dietary_goals = [
        "General Balanced Diet", "Weight Loss", "Weight Gain / Muscle Building", 
        "Heart Health (Low Cholesterol)", "Diabetes Management", "Athletic Performance",
        "Cold / Immune Boost", "Nutrient Booster"
    ]
    
    current_dietary_goal = st.session_state.dietary_goal_selected
    if current_dietary_goal is None or current_dietary_goal not in dietary_goals:
        current_dietary_goal = dietary_goals[0]
    
    goal_index = dietary_goals.index(current_dietary_goal)
    goal = st.selectbox(
        "Select your primary health goal for this plan:", 
        dietary_goals, 
        index=goal_index, 
        key="goal_select"
    )

    boosted_nutrients = []
    if goal == "Nutrient Booster":
        available_to_boost = ["Iron", "Calcium", "Potassium", "Vitamin A", "Niacin", "Vitamin C", "Fiber"]
        boosted_nutrients = st.multiselect("Select nutrients to boost (a 50% boost will be applied):", available_to_boost, default=st.session_state.boosted_nutrients_selected)

    # --- REPLACED: Radio button with a slider ---
    st.subheader("Choose Your Plan Preference")
    variety_level = st.slider(
        "Adjust the trade-off between plan cost and food variety.",
        min_value=1,
        max_value=5,
        value=st.session_state.get('variety_cost_level', 3),
        format="%d",
        help=(
            "**1 (Lowest Cost):** The absolute cheapest plan, likely with high food repetition.\n\n"
            "**3 (Balanced):** A moderate-cost plan with good daily variety.\n\n"
            "**5 (Highest Variety):** A plan with the most unique foods possible, which will be more expensive."
        ),
        key='variety_cost_level_slider'
    )
    
    level_labels = {
        1: "Lowest Cost",
        2: "Cost-Focused",
        3: "Balanced",
        4: "Variety-Focused",
        5: "Highest Variety"
    }
    st.info(f"**Selected Preference: Level {variety_level} ({level_labels[variety_level]})**")


    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Previous: Your Profile", on_click=ui_utils.go_to_page, args=("Step 1: Your Profile",), use_container_width=True)

    with col2:
        if st.button("Save Plan Goals & Proceed ➡️", type="primary", use_container_width=True):
            st.session_state.dietary_goal_selected = goal
            st.session_state.boosted_nutrients_selected = boosted_nutrients
            st.session_state.variety_cost_level = variety_level
            st.session_state.plan_results = None
            st.success(f"Goals saved! Dietary Goal: **{goal}**, Plan Preference: **{level_labels[variety_level]}**.")
            ui_utils.go_to_page("Step 3: Customize Plan Details")
            st.rerun()

    if st.session_state.dietary_goal_selected:
        st.info(f"Current Goals: Dietary Goal: **{st.session_state.dietary_goal_selected}**, Plan Preference: **{level_labels[st.session_state.variety_cost_level]}**.")