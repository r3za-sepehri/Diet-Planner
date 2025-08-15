import streamlit as st
from pulp import LpStatus, listSolvers, getSolver

# Import core logic and data loader
from core import data_loader, requirements_calculator, optimizer, ai_planner

# Import the new UI page modules
from ui_pages import (
    profile,
    goals,
    customize,
    view_plan,
    add_food,
    update_prices,
    help
)

# -----------------------------------------------------------------------------
# Page Configuration and Data Loading
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Diet Optimization Program",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Loads and cleans all necessary data, caching the result."""
    try:
        (nutrition_df, prices_series, intake_df, food_group_map, coffee_df) = data_loader.load_and_clean_data()
        unique_groups = sorted(list(set(food_group_map.values())))
        all_foods = sorted(nutrition_df.index.tolist())
        return nutrition_df, prices_series, intake_df, food_group_map, unique_groups, all_foods, coffee_df
    except Exception as e:
        st.error(f"Fatal Error: Could not load initial data: {e}")
        st.error("Please ensure the 'data' directory and its CSV files are correctly placed.")
        return None, None, None, None, None, None, None

# Load the data
NUTRITION_DATA, PRICES, INTAKE_REQS, FOOD_GROUPS_MAP, UNIQUE_GROUPS, ALL_FOODS, COFFEE_DATA = load_data()

# Initialize Streamlit's session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {'num_meals': 3, 'num_snacks': 2, 'weight_kg': 70}
if 'nutrient_reqs' not in st.session_state:
    st.session_state.nutrient_reqs = None
if 'dietary_goal_selected' not in st.session_state:
    st.session_state.dietary_goal_selected = None
if 'boosted_nutrients_selected' not in st.session_state:
    st.session_state.boosted_nutrients_selected = []
# --- REPLACED: strategy with variety level ---
if 'variety_cost_level' not in st.session_state:
    st.session_state.variety_cost_level = 3 # Default to "Balanced"
if 'plan_results' not in st.session_state:
    st.session_state.plan_results = None
if 'plan_source' not in st.session_state:
    st.session_state.plan_source = ""
if 'custom_prices' not in st.session_state:
    st.session_state.custom_prices = {}
if 'include_list' not in st.session_state:
    st.session_state.include_list = []
if 'exclude_list' not in st.session_state:
    st.session_state.exclude_list = []
if 'custom_foods' not in st.session_state:
    st.session_state.custom_foods = []
if 'page_selection' not in st.session_state:
    st.session_state.page_selection = "Step 1: Your Profile"
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False
if 'ai_cuisine' not in st.session_state:
    st.session_state.ai_cuisine = "Any"
if 'ai_cook_time' not in st.session_state:
    st.session_state.ai_cook_time = 30
if 'ai_custom_instructions' not in st.session_state:
    st.session_state.ai_custom_instructions = ""

# -----------------------------------------------------------------------------
# Welcome Popup Logic
# -----------------------------------------------------------------------------

def show_welcome_popup():
    """Displays a welcome dialog for first-time users of the session."""
    @st.dialog("Welcome to the Diet Planner!")
    def welcome():
        st.markdown(
            "It looks like this is your first time here. For the best experience, "
            "we recommend taking a quick look at the tutorial to understand how the "
            "planning process works."
        )
        col1, col2 = st.columns(2)
        if col1.button("Take me to the Tutorial!", use_container_width=True, type="primary"):
            st.session_state.page_selection = "About / Help"
            st.rerun()
        if col2.button("Continue to the App", use_container_width=True):
            st.rerun()

    welcome()

if 'welcome_popup_shown' not in st.session_state:
    show_welcome_popup()
    st.session_state.welcome_popup_shown = True

# -----------------------------------------------------------------------------
# Main Application Logic & Sidebar
# -----------------------------------------------------------------------------

st.sidebar.title("🍎 Diet Planner")
st.sidebar.markdown("---")

st.sidebar.header("Main Workflow")

workflow_pages = [
    "Step 1: Your Profile",
    "Step 2: Select Plan Goals",
    "Step 3: Customize Plan Details",
    "Step 4: View Plan & Generate Prompts"
]
workflow_captions = [
    "Calculate your needs",
    "Choose dietary & optimization goals",
    "Fine-tune food choices & generate plan",
    "View plan & create AI prompts"
]

def update_page_from_radio():
    st.session_state.page_selection = st.session_state.workflow_radio

current_page_selection = st.session_state.page_selection
if current_page_selection not in workflow_pages:
    current_page_index = 3 
else:
    current_page_index = workflow_pages.index(current_page_selection)

st.sidebar.radio(
    "Workflow Steps",
    options=workflow_pages,
    captions=workflow_captions,
    key='workflow_radio',
    index=current_page_index,
    on_change=update_page_from_radio
)

st.sidebar.markdown("---")
st.sidebar.header("Tools & Settings")
if st.sidebar.button("Add Custom Food", use_container_width=True):
    st.session_state.page_selection = "Add Custom Food"
    st.rerun()
if st.sidebar.button("Update Food Prices", use_container_width=True):
    st.session_state.page_selection = "Update Food Prices"
    st.rerun()
if st.sidebar.button("About / Help", use_container_width=True):
    st.session_state.page_selection = "About / Help"
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Status**")
if st.session_state.nutrient_reqs is not None:
    st.sidebar.success("✅ Step 1: Profile Complete")
else:
    st.sidebar.warning("⚪ Step 1: Profile Incomplete")

if st.session_state.dietary_goal_selected:
    st.sidebar.success("✅ Step 2: Goals Selected")
else:
    st.sidebar.warning("⚪ Step 2: Goals Not Selected")

if st.session_state.plan_results:
    st.sidebar.success("✅ Step 3: Plan Generated")
    st.sidebar.success("✅ Step 4: Plan Ready to View")
else:
    st.sidebar.warning("⚪ Step 3: Plan Not Generated")
    st.sidebar.warning("⚪ Step 4: Plan Not Ready")
st.sidebar.markdown("---")

# Page routing
if st.session_state.page_selection == "Step 1: Your Profile":
    profile.display_profile_page(INTAKE_REQS, requirements_calculator)
elif st.session_state.page_selection == "Step 2: Select Plan Goals":
    goals.display_select_plan_goals_page()
elif st.session_state.page_selection == "Step 3: Customize Plan Details":
    customize.display_customize_plan_details_page(
        NUTRITION_DATA, PRICES, FOOD_GROUPS_MAP, COFFEE_DATA, 
        requirements_calculator, optimizer, LpStatus, listSolvers, getSolver
    )
elif st.session_state.page_selection == "Step 4: View Plan & Generate Prompts":
    view_plan.display_plan_and_prompt_page(PRICES, ai_planner)
elif st.session_state.page_selection == "Add Custom Food":
    add_food.display_add_food_page(UNIQUE_GROUPS, NUTRITION_DATA, ALL_FOODS)
elif st.session_state.page_selection == "Update Food Prices":
    update_prices.display_price_update_page(ALL_FOODS, PRICES)
elif st.session_state.page_selection == "About / Help":
    help.display_help_page()