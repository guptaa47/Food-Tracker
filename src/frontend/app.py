import json
import pandas as pd
import streamlit as st
import backend.services.search as search

# maybe use streamlit_keyup for instant text updates

if 'food_nutrients' not in st.session_state:
    st.session_state['food_nutrients'] = None

if 'meal' not in st.session_state:
    st.session_state['meal'] = []

PRIORITIES = [
    "total_energy (kcals)",
    "total_protein",
    "total_fat",
    "total_sugars",
    "starch",
    "moisture"
]


st.sidebar.success('Select a page')

st.title('Food Search')

query = st.text_input('Search foods')


if query:
    if len(query) == 1:
        st.write("Please enter at least two letters")
    else:
        results = search.search_food(query)

        if len(results) == 0:
            st.write("No foods found matching your search")
        else:
            st.write(f"Found {len(results)} results")

            food_names = [r['name'] for r in results]
            # selected_food = st.radio("Select a food to see nutrients", food_names)
            selected_food = st.selectbox(
                "Select a food",
                options=food_names,
            )

            nutrients = search.get_nutrients(selected_food)
            st.session_state['food_nutrients'] = nutrients
        
if st.session_state['food_nutrients']:
    quantity = st.number_input('# grams', min_value=0.0, value=100.0, step=1.0)
    nutrients = st.session_state['food_nutrients']
    st.subheader(f"Nutrients for {nutrients[0]['food_name']}")
    # Convert to dataframe for nice table
    df = pd.DataFrame(nutrients)
    df = df[['nutrient_name', 'value']]
    df['value'] = df['value'].astype(float) * quantity / 100
    df.loc[df['nutrient_name'] == 'total_energy', 'value'] /= 4.184
    df.loc[df['nutrient_name'] == 'total_energy', 'nutrient_name'] += " (kcals)"
    df = df[df['value'] != 0]
    df = df.rename(columns={'nutrient_name': 'Nutrient', 'value': 'Amount (g)'})
    df["idx"] = df.index
    df["priority"] = df["Nutrient"].apply(
        lambda x: PRIORITIES.index(x) if x in PRIORITIES else len(PRIORITIES)
    )
    df = df.sort_values(["priority", "idx"]).drop(columns=["priority", "idx"])
    
    st.table(df, hide_index=True)

    if st.button("Add to meal"):
        st.session_state['meal'].append({
            "name": selected_food,
            "quantity": quantity,
            "nutrients": nutrients
        })
else:
    st.info("No nutrient data found.")


st.divider()
st.header("Current Meal")

meal = st.session_state['meal']

if len(meal) == 0:
    st.write("No foods added yet.")
else:
    for i, item in enumerate(meal):
        st.write(f"{item['name']} — {item['quantity']} g")

        # remove button
        if st.button(f"Remove {item['name']}", key=f"remove_{i}"):
            st.session_state['meal'].pop(i)
            st.rerun()

if len(meal) > 0:
    combined = {}
    nutrient_sets = [{n['nutrient_name'] for n in item['nutrients']} for item in meal]
    common_nutrients = set.intersection(*nutrient_sets)

    for item in meal:
        for n in item['nutrients']:
            name = n['nutrient_name']
            value = float(n['value']) * item['quantity'] / 100
            
            if name not in common_nutrients:
                continue

            if name == 'total_energy':
                name += ' (kcals)'
                value /= 4.184

            if name not in combined:
                combined[name] = 0
            combined[name] += value

    df_meal = pd.DataFrame([
        {"Nutrient": k, "Total Amount (g)": v}
        for k, v in combined.items()
        if v != 0
    ])

    df_meal["idx"] = df_meal.index
    df_meal["priority"] = df_meal["Nutrient"].apply(
        lambda x: PRIORITIES.index(x) if x in PRIORITIES else len(PRIORITIES)
    )
    df_meal = df_meal.sort_values(["priority", "idx"]).drop(columns=["priority", "idx"])

    st.subheader("Total Meal Nutrients")
    st.table(df_meal, hide_index=True)

if st.button("Clear meal"):
    st.session_state['meal'] = []
    st.rerun()

if st.button("Save Meal"):
    with open("outputs/saved_meals.json", "a") as f:
        json.dump(st.session_state['meal'], f)
        f.write("\n")
    st.success("Meal saved!")
