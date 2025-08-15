import streamlit as st
import pandas as pd
from . import ui_utils

def display_customize_plan_details_page(
    NUTRITION_DATA, PRICES, FOOD_GROUPS_MAP, COFFEE_DATA, 
    requirements_calculator, optimizer, LpStatus, listSolvers, getSolver
):
    """Renders the UI for Step 3: Customizing Plan Details and Generating Plan."""
    st.header("Step 3: Customize Plan Details", divider='rainbow')

    if st.session_state.nutrient_reqs is None or st.session_state.get('variety_cost_level') is None:
        st.warning("Please complete Steps 1 and 2 before proceeding to plan customization.")
        if st.button("Go back to Step 1"): ui_utils.go_to_page("Step 1: Your Profile")
        if st.button("Go back to Step 2"): ui_utils.go_to_page("Step 2: Select Plan Goals")
        return

    level_labels = {1: "Lowest Cost", 2: "Cost-Focused", 3: "Balanced", 4: "Variety-Focused", 5: "Highest Variety"}
    plan_preference = level_labels[st.session_state.variety_cost_level]
    st.info(f"You've selected a **{plan_preference}** plan for **{st.session_state.dietary_goal_selected}**.")

    try:
        reqs_with_goal = requirements_calculator.apply_dietary_goal_adjustments(
            st.session_state.nutrient_reqs, 
            st.session_state.dietary_goal_selected, 
            weight_kg=st.session_state.user_data['weight_kg'],
            boosted_nutrients=st.session_state.boosted_nutrients_selected
        )
    except Exception as e:
        st.error(f"Could not apply dietary goal: {e}")
        reqs_with_goal = st.session_state.nutrient_reqs

    nutrition_df_for_optimizer = NUTRITION_DATA.copy()
    prices_for_optimizer = PRICES.copy()
    food_groups_for_optimizer = FOOD_GROUPS_MAP.copy()
    
    if st.session_state.custom_foods:
        custom_nut_df = pd.DataFrame([f['nutrients'] for f in st.session_state.custom_foods], index=[f['name'] for f in st.session_state.custom_foods])
        nutrition_df_for_optimizer = pd.concat([nutrition_df_for_optimizer, custom_nut_df])
        for food in st.session_state.custom_foods:
            prices_for_optimizer[food['name']] = food['price_per_gram']
            food_groups_for_optimizer[food['name']] = food['group']
    all_foods_for_optimizer = sorted(nutrition_df_for_optimizer.index.tolist())

    drinks_coffee_key = f"drinks_coffee_{st.session_state.variety_cost_level}"
    coffee_type_key = f"coffee_type_{st.session_state.variety_cost_level}"
    cups_per_day_key = f"cups_per_day_{st.session_state.variety_cost_level}"
    
    if COFFEE_DATA is not None:
        with st.expander("Coffee Consumption (Optional)"):
            drinks_coffee = st.radio("Do you drink coffee?", ("No", "Yes"), key=drinks_coffee_key, horizontal=True)
            if drinks_coffee == "Yes":
                coffee_type = st.selectbox("Type of coffee:", options=COFFEE_DATA.index.tolist(), key=coffee_type_key)
                cups_per_day = st.number_input("Cups per day:", min_value=1, max_value=10, value=1, key=cups_per_day_key)

    def food_selection_ui(key_prefix):
        st.markdown("---")
        st.subheader("Customize Food Selection")
        with st.expander("How does this work?"):
            st.caption(
                "Use these lists to guide the optimizer. This is useful for including favorite foods or excluding allergens and dislikes.\n\n"
                "- **Always Include:** The optimizer will be forced to use at least some amount of every food on this list in the weekly plan.\n\n"
                "- **Always Exclude:** The optimizer will be forbidden from using any food on this list."
            )
        
        available_foods = [f for f in all_foods_for_optimizer if f not in st.session_state.include_list and f not in st.session_state.exclude_list]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Add Foods to Lists")
            food_to_add = st.selectbox("Search for a food", options=[""] + sorted([ui_utils._format_name(f) for f in available_foods]), key=f"{key_prefix}_food_search", label_visibility="collapsed")
            sub_col1, sub_col2 = st.columns(2)
            if sub_col1.button("Add to Include >>", use_container_width=True, key=f"{key_prefix}_include_search"):
                ui_utils.add_to_list('include_list', ui_utils._unformat_name(food_to_add)); st.rerun()
            if sub_col2.button("Add to Exclude >>", use_container_width=True, key=f"{key_prefix}_exclude_search"):
                ui_utils.add_to_list('exclude_list', ui_utils._unformat_name(food_to_add)); st.rerun()
        with col2:
            st.markdown("##### Current Selections")
            st.markdown("<p style='color:green; font-weight:bold;'>Always Include:</p>", unsafe_allow_html=True)
            if not st.session_state.include_list: st.caption("No foods specified.")
            else:
                for food in st.session_state.include_list:
                    r_col1, r_col2 = st.columns([0.9, 0.1])
                    r_col1.write(f"- {ui_utils._format_name(food)}")
                    r_col2.button("🗑️", key=f"{key_prefix}_remove_include_{food}", on_click=ui_utils.remove_from_list, args=('include_list', food), help="Remove this food")
            st.markdown("---")
            st.markdown("<p style='color:red; font-weight:bold;'>Always Exclude:</p>", unsafe_allow_html=True)
            if not st.session_state.exclude_list: st.caption("No foods specified.")
            else:
                for food in st.session_state.exclude_list:
                    r_col1, r_col2 = st.columns([0.9, 0.1])
                    r_col1.write(f"- {ui_utils._format_name(food)}")
                    r_col2.button("🗑️", key=f"{key_prefix}_remove_exclude_{food}", on_click=ui_utils.remove_from_list, args=('exclude_list', food), help="Remove this food")

    food_selection_ui(key_prefix=st.session_state.variety_cost_level)

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅️ Previous: Select Plan Goals", on_click=ui_utils.go_to_page, args=("Step 2: Select Plan Goals",), use_container_width=True)
        
    with col2:
        generate_button_label = f"Generate {plan_preference} Plan"
        if st.button(generate_button_label, type="primary", use_container_width=True):
            # --- UPDATED: Display multiple facts in a styled box inside the spinner ---
            facts = [ui_utils.get_random_food_fact() for _ in range(34)]
            fact_markdown = "#### 🧠 Did You Know?\n" + "\n".join([f"- *{fact}*" for fact in facts])
            
            with st.spinner(f"🧠 Optimizing for {plan_preference.upper()}... This may take up to 3 minutes."):
                st.info(fact_markdown)
                try:
                    intake_reqs_for_optimizer = reqs_with_goal.copy()

                    if COFFEE_DATA is not None and st.session_state.get(drinks_coffee_key) == "Yes":
                        coffee_nutrients = COFFEE_DATA.loc[st.session_state[coffee_type_key]]
                        nutrient_map = {'calories': 'calorie', 'potassium_mg': 'potassium', 'niacin_mg': 'niacin'}
                        for coffee_col, intake_col in nutrient_map.items():
                            if intake_col in intake_reqs_for_optimizer.index and coffee_col in coffee_nutrients.index:
                                total_from_coffee = coffee_nutrients[coffee_col] * st.session_state[cups_per_day_key]
                                intake_reqs_for_optimizer.loc[intake_col, 'lower_bound'] -= total_from_coffee
                        intake_reqs_for_optimizer['lower_bound'] = intake_reqs_for_optimizer['lower_bound'].clip(lower=0)
                    
                    effective_prices = prices_for_optimizer.copy()
                    if st.session_state.custom_prices:
                        for food, price in st.session_state.custom_prices.items():
                            if food in effective_prices.index: effective_prices.loc[food] = price
                    
                    effective_exclude_list = st.session_state.exclude_list.copy()
                    if st.session_state.dietary_goal_selected == "Heart Health (Low Cholesterol)":
                        other_oils = ['canolla_oil', 'corn_oil', 'sunseed_oil']
                        for oil in other_oils:
                            if oil not in effective_exclude_list:
                                effective_exclude_list.append(oil)

                    prob, gram_vars, days = optimizer.create_and_solve_model(
                        nutrition_df=nutrition_df_for_optimizer, prices_series=effective_prices, intake_df=intake_reqs_for_optimizer, food_group_map=food_groups_for_optimizer,
                        foods_to_exclude=effective_exclude_list, 
                        foods_to_include=st.session_state.include_list,
                        daily_diversity_target=st.session_state.user_data['num_meals'] + st.session_state.user_data['num_snacks'],
                        days_of_week=7, nutrient_mode='daily', 
                        variety_level=st.session_state.variety_cost_level,
                        solver_name=getSolver(listSolvers(onlyAvailable=True)[0], timeLimit=180)
                    )

                    status = LpStatus[prob.status]
                    if status in ('Optimal', 'Not Solved'):
                        solution = {d: {f_key: var.varValue for (f_key, d_key), var in gram_vars.items() if d_key == d and var.varValue > 0.01} for d in days}
                        st.session_state.plan_results = solution
                        st.session_state.plan_source = f"{plan_preference} Plan"
                        st.success("Optimization successful! Your plan is ready in Step 4.")
                        st.session_state.scroll_to_top = True
                        ui_utils.go_to_page("Step 4: View Plan & Generate Prompts")
                        st.rerun()
                    else:
                        st.session_state.plan_results = None
                        st.error("Could not find an optimal solution. The constraints might be too strict. Try a lower variety level or adjust your food selections.")

                except Exception as e:
                    st.error(f"An optimization error occurred: {e}")