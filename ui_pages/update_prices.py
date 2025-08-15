import streamlit as st
import pandas as pd
from . import ui_utils

def display_price_update_page(ALL_FOODS, PRICES):
    st.header("Update Food Prices", divider='rainbow')
    st.markdown("Here you can override the default food prices. The 'Cost-Optimized Plan' will use these new prices.")
    with st.form("price_update_form"):
        food_to_update = st.selectbox("Select Food to Update", options=sorted([ui_utils._format_name(f) for f in ALL_FOODS]))
        weight_g = st.number_input("Weight (in grams)", min_value=1.0, value=100.0)
        price_for_weight = st.number_input("Price for this weight", min_value=0.01, value=5.0, format="%.2f")
        submitted = st.form_submit_button("Update Price")
    if submitted and food_to_update:
        internal_name = ui_utils._unformat_name(food_to_update)
        st.session_state.custom_prices[internal_name] = price_for_weight / weight_g
        st.success(f"Updated price for '{food_to_update}'.")
    if st.session_state.custom_prices:
        st.subheader("Current Custom Prices")
        custom_price_data = [{"Food Item": ui_utils._format_name(food), "Custom Price per Gram": f"{ppg:.4f}", "Original Price per Gram": f"{PRICES.get(food, 0):.4f}"} for food, ppg in st.session_state.custom_prices.items()]
        st.dataframe(pd.DataFrame(custom_price_data), use_container_width=True, hide_index=True)
        if st.button("Reset All Custom Prices"): st.session_state.custom_prices = {}; st.rerun()
    else: st.info("No custom prices have been set.")