import json

def get_vehicle_specs(brand: str, model: str, year: int, text_model):
    try:
        prompt = f"""
        Please provide detailed specifications for a {year} {brand} {model}.
        Include:
        1. Brand
        2. Model
        3. Year
        4. Fuel consumption (liters/100km)
        5. Engine size (cc)
        6. Number of cylinders
        7. Transmission type
        8. Fuel type
        9. Horsepower
        10. Torque (Nm)
        11. Top speed (km/h)
        12. Acceleration 0-100 km/h (seconds)
        13. Price range (USD)
        14. Safety features
        15. Comfort features
        16. Technology features
        
        Format the response as a JSON object with this structure:
        {{
            "brand": "{brand}",
            "model": "{model}",
            "year": {year},
            "fuel_consumption": float,
            "engine_size": integer,
            "cylinders": integer,
            "transmission": "string",
            "fuel_type": "string",
            "horsepower": integer,
            "torque": integer,
            "top_speed": integer,
            "acceleration": float,
            "price_range": "string",
            "safety_features": ["string"],
            "comfort_features": ["string"],
            "technology_features": ["string"]
        }}
        
        Important:
        - Return ONLY the JSON object, no additional text
        - Use exact values for brand, model, and year as provided
        - Ensure all numeric values are actual numbers, not strings
        - If any value is unknown, use null
        """
        
        response = text_model.generate_content(prompt)
        
        if not response or not response.text:
            raise Exception("Received empty response from Gemini")
        
        # Clean the response text
        cleaned_text = response.text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        # Parse the response as JSON
        specs = json.loads(cleaned_text)
        return specs
    except Exception as e:
        raise Exception(f"Error getting vehicle specs: {e}") 