# app.py

import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Load Environment Variables ---
# Best practice: store your API key in a .env file
load_dotenv()

# --- Gemini API Configuration ---
# Configure the API key from the environment variable
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    raise RuntimeError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")

# --- Pydantic Model for Request Validation ---
class IngredientRequest(BaseModel):
    ingredient_name: str

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Ingredient Inspector AI (Gemini Edition)",
    description="API for analyzing skincare ingredients using the Gemini API."
)

# --- Core Logic in the API Endpoint ---
@app.post("/analyze")
async def analyze_ingredient(request: IngredientRequest):
    """
    Accepts a skincare ingredient, sends it to the Gemini API for analysis,
    and returns a structured JSON response.
    """
    ingredient = request.ingredient_name
    
    # 1. Define the generation config to enforce JSON output.
    # This is a reliable feature of the Gemini API.
    generation_config = genai.GenerationConfig(response_mime_type="application/json")
    
    # 2. Initialize the Gemini Pro model.
    model = genai.GenerativeModel("models/gemini-1.5-flash", generation_config=generation_config)
                         
    # 3. Get the prompt. The prompt is slightly simplified as the API now enforces JSON.
    prompt = get_llm_prompt(ingredient)
    
    try:
        # 4. Call the Gemini API.
        response = await model.generate_content_async(prompt)

        # 5. Parse the LLM's string response into a JSON object.
        json_response = json.loads(response.text)
        
        return json_response

    except json.JSONDecodeError:
        # This handles cases where the LLM might still fail to return perfect JSON.
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: The API returned a malformed JSON response."
        )
    except Exception as e:
        # Handle other potential errors (e.g., API authentication, connection issues).
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred with the Gemini API: {str(e)}"
        )

def get_llm_prompt(ingredient_name: str) -> str:
    """
    Generates the prompt for the Gemini API.
    It describes the desired JSON schema and provides the ingredient.
    """
    prompt = f"""
Analyze the skincare ingredient: "{ingredient_name}"

Provide your analysis in a JSON object with the following schema:
- "purpose": A brief description of the ingredient's function.
- "safety_rating": A rating which must be one of "Safe", "Caution", or "Avoid".
- "notes": A single, concise sentence explaining potential risks or considerations.
"""
    return prompt.strip()