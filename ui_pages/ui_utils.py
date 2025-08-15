import streamlit as st
import random
import os
import math

def _format_name(name):
    return name.replace('_', ' ').title()

def _unformat_name(formatted_name):
    return formatted_name.replace(' ', '_').lower()

def add_to_list(list_name, food_item):
    if food_item and food_item not in st.session_state[list_name]:
        st.session_state[list_name].append(food_item)

def remove_from_list(list_name, food_item):
    if food_item in st.session_state[list_name]:
        st.session_state[list_name].remove(food_item)

def go_to_page(page_name):
    """Callback function to change the page in the sidebar."""
    st.session_state.page_selection = page_name

# --- REPLACED: New smart rounding function ---
def smart_round_grams(n):
    """
    Applies intelligent rounding to gram amounts for practical kitchen use.
    - Minimum is 10g.
    - Rounds up to the nearest 5 for values between 10g and 20g.
    - Rounds to the nearest 5 for values >= 20g.
    """
    if n < 10:
        return 10
    if n < 20:
        return int(math.ceil(n / 5.0) * 5)
    return int(round(n / 5.0) * 5)

def get_random_food_fact():
    """Reads and returns a single random line from the food_facts.txt file."""
    try:
        fact_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'food_facts.txt')
        with open(fact_file, 'r', encoding='utf-8') as f:
            facts = [line.strip() for line in f if line.strip()]
        return random.choice(facts)
    except (FileNotFoundError, IndexError):
        return "A colorful plate with a variety of vegetables is a great sign of a healthy meal!"