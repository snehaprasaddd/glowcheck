import streamlit as st
import requests

# Define the URL of your running FastAPI backend
API_URL = "http://127.0.0.1:8000/analyze"

# --- Streamlit User Interface ---

st.title("🧪 Ingredient Inspector AI")
st.markdown("Analyze skincare ingredients using AI. Just paste a list of ingredients below.")

# 1. Text area for user input
ingredients_text = st.text_area(
    "Paste your ingredient list here, separated by commas",
    "Niacinamide, Retinol, Hyaluronic Acid, Ceteareth-20",
    height=150
)

# 2. Button to trigger the analysis
if st.button("Analyze Ingredients"):
    # Check if the text area is empty
    if not ingredients_text.strip():
        st.warning("Please enter at least one ingredient to analyze.")
    else:
        # Split the input text into a list of individual ingredients
        # The list comprehension cleans up whitespace and removes any empty items
        ingredients_list = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]

        # Display a spinner while processing
        with st.spinner(f"Analyzing {len(ingredients_list)} ingredients..."):
            # Loop through each ingredient and call the backend API
            for ingredient in ingredients_list:
                try:
                    # Make the POST request to the FastAPI backend
                    response = requests.post(API_URL, json={"ingredient_name": ingredient})

                    # Check if the request was successful
                    if response.status_code == 200:
                        data = response.json()
                        safety_rating = data.get("safety_rating", "Unknown")
                        purpose = data.get("purpose", "No purpose specified.")
                        notes = data.get("notes", "No notes available.")

                        # Display a subheader for the ingredient
                        st.subheader(ingredient)

                        # Bonus: Use status elements based on safety_rating
                        if safety_rating == "Safe":
                            st.success(f"**Rating: Safe**")
                        elif safety_rating == "Caution":
                            st.warning(f"**Rating: Caution**")
                        elif safety_rating == "Avoid":
                            st.error(f"**Rating: Avoid**")
                        
                        # Display the purpose and notes
                        st.markdown(f"**Purpose:** {purpose}")
                        st.markdown(f"**Notes:** {notes}")

                    else:
                        st.error(f"Error analyzing '{ingredient}': Received status code {response.status_code}")

                except requests.exceptions.ConnectionError:
                    st.error(
                        "**Connection Error:** Could not connect to the backend API. "
                        "Please make sure your FastAPI server (`app.py`) is running in a separate terminal."
                    )
                    break  # Stop the loop if the backend is not reachable
                except Exception as e:
                    st.error(f"An unexpected error occurred for '{ingredient}': {e}")
                
                st.markdown("---") # Visual separator for each ingredient