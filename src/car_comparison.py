import json
import google.generativeai as genai

def compare_cars(car1_specs, car2_specs, model):
    try:
        prompt = f"""
        Compare these two cars and provide a detailed analysis:
        
        Car 1:
        {json.dumps(car1_specs, indent=2)}
        
        Car 2:
        {json.dumps(car2_specs, indent=2)}
        
        Provide the comparison in the following format:
        1. Overall Comparison
        2. Performance Comparison
        3. Technical Specifications
        4. Pros and Cons of each car
        5. Recommendation based on different use cases
        
        Format the response in a clear, structured way with bullet points and clear sections.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Error comparing cars: {str(e)}")

def get_car_specs(brand: str, model: str, year: int, text_model):
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
        
        Format the response as a JSON object.
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
        raise Exception(f"Error getting car specs: {e}") 