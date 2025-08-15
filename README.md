# Diet Optimization Program

This application provides a comprehensive tool for creating nutritionally balanced and cost-optimized weekly diet plans based on personal data and food preferences.

It leverages mathematical optimization to generate food lists. It then helps you create a detailed prompt to use with an AI assistant (like Google Gemini or ChatGPT) to transform those lists into practical, creative meal plans complete with recipes.

## How to Use the Program (Tutorial)

The program is organized into a simple workflow. Follow the steps in the "Main Workflow" section of the navigation panel on the left.

### Step 1: Your Profile
This is the most important step. The accuracy of your diet plan depends on the information you provide here.

-   **Personal Data:** Enter your age, gender, weight, and height.
-   **Meals/Snacks:** Tell the program how you like to structure your day. This helps the optimizer create a diverse plan and helps the AI build a meal schedule.
-   **Physical Activity Level:** Select the option that best describes your weekly routine. Hover over the question mark (`?`) for a detailed guide.
-   **Pregnancy/Lactation:** If applicable, select the appropriate status.

Click **"Save Profile & Calculate Needs"** when you are done. The program will automatically take you to Step 2. A green checkmark (✅) will appear next to Step 1 in the sidebar.

### Step 2: Select Plan Goals
Here, you'll define the high-level objectives for your diet plan.

-   **Dietary Goal:** Choose a primary health goal, such as "Weight Loss" or "Heart Health." This adjusts your nutritional targets.
-   **Plan Preference:** Use the slider to choose your desired balance between cost and food variety.
    -   **Level 1 (Lowest Cost):** Finds the absolute cheapest plan, which may have very repetitive meals.
    -   **Level 3 (Balanced):** A moderate-cost plan with good daily variety (Recommended).
    -   **Level 5 (Highest Variety):** A plan with the most unique foods possible, which will be more expensive.

Click **"Save Plan Goals & Proceed"** to lock in your choices and automatically move to the next step.

#### Understanding Your Dietary Goals

-   **General Balanced Diet:** Uses your calculated daily needs without modification.
-   **Weight Loss:** Creates a calorie deficit by reducing daily intake by **500 kcal** (or to a minimum of 1200 kcal) and increases protein by **20%** to help preserve muscle.
-   **Weight Gain / Muscle Building:** Creates a calorie surplus by increasing daily intake by **500 kcal** and sets a high protein target (**~1.6 g/kg** of body weight) to support muscle growth.
-   **Heart Health (Low Cholesterol):** Increases the minimum daily fiber target to **35g** and limits saturated fat to less than **10%** of total calories to support cardiovascular health.
-   **Diabetes Management:** Increases the minimum daily fiber target to **40g** to help manage blood sugar levels.
-   **Athletic Performance:** Increases the protein target to **~1.4 g/kg** of body weight to support recovery and performance.
-   **Cold / Immune Boost:** Triples the minimum daily **Vitamin C** requirement to support immune function.
-   **Nutrient Booster:** Allows you to manually select specific vitamins and minerals to increase their minimum requirements.

### Step 3: Customize Plan Details
This is where you fine-tune the plan and generate your weekly food list.

-   **Coffee Consumption (Optional):** Account for your daily coffee habit so the optimizer can adjust your nutrient targets accordingly.
-   **Customize Food Selection:** Force the optimizer to **include** certain foods you love or **exclude** others you dislike or are allergic to.
-   **Generate Plan:** Once you have set your preferences, click the large **"Generate Plan"** button. After a moment, the program will run the optimization and automatically take you to Step 4 to view the results.

### Step 4: View Plan & Generate Prompts
This is the final step, where you can review your complete plan and get the tools to turn it into meals.

-   **Plan Summary:** At the top, you'll see the key outcomes of your plan, such as the **Estimated Weekly Cost** and the **Total Unique Foods**, which directly reflect the preference you set in Step 2.
-   **Your Weekly Plan & Shopping List:** In the first section, you can view the total shopping list for the week and see a day-by-day breakdown of the foods and quantities required.
-   **Get AI Prompts for Meal Planning:** In the second section, you can customize the AI's instructions to match your tastes. You can select a preferred **cuisine style**, set a **maximum cooking time**, and provide **custom notes** (e.g., "I don't like spicy food"). Once customized, click the tabs for each day, copy the tailored prompt, and paste it into an AI chat interface to get your creative meal plan.

## Tools & Settings

In the sidebar, you will find additional pages to customize your experience:

-   **Add Custom Food:** Add new foods to the program's database for this session.
-   **Update Food Prices:** Set your own local prices for foods to get a more accurate cost optimization.
-   **About / Help:** Displays this guide.

## A Note on Collaboration: The Human-AI Partnership

This application was developed using a modern, collaborative "pair-programming" model between a human lead and an AI assistant. This section clarifies the roles to provide transparency on how the project was built.

### The Project Lead: Mohammad Reza Sepehri

As the lead, Mohammad Reza served as the architect and director of the project. His responsibilities included:

-   **Vision and Conception:** He conceived the original idea for the Diet Planner.
-   **Feature Design:** He defined the "what"—deciding the program's core functionalities, the user workflow (from profiling to AI prompts), and the overall user experience.
-   **Guidance and Direction:** He provided the AI with specific requirements, instructions, and high-level logic for every feature.
-   **Testing and Validation:** He was responsible for all testing, identifying bugs, and ensuring the final product was correct, functional, and aligned with his vision.

Essentially, the human provided the creative intelligence, the project goals, and the quality control.

### The AI Pair-Programmer: Google AI Studio

**Google AI Studio** served as a powerful tool and a "driver" in the pair-programming relationship. Its role was to execute the technical tasks based on the human lead's directives. Its responsibilities included:

-   **Code Generation:** Writing the Python code to implement the features as specified.
-   **Refactoring:** Cleaning up and restructuring the code for better readability and maintenance.
-   **Bug Fixing:** Identifying and correcting errors in the code based on testing feedback.
-   **Documentation:** Generating comments and help text based on the program's functionality.

Essentially, the AI provided the "how"—translating the human's vision and requirements into functional code with speed and accuracy. This synergy allowed for the rapid development of a complex and polished application.