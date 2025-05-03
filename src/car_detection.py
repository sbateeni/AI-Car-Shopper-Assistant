import google.generativeai as genai
from PIL import Image
import io
import re
import json

def detect_car(image, vision_model):
    try:
        # Convert image to RGB if it's in RGBA mode
        if image.mode == 'RGBA':
            image = image.convert('RGB')
            
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Prepare the prompt
        prompt = """
        Analyze this car image and provide the following information in a structured format:
        Make: [brand]
        Model: [model]
        Year: [year]
        Type: [vehicle type]
        
        Be specific about the model and year if possible.
        """
        
        # Get response from Gemini
        response = vision_model.generate_content([prompt, Image.open(io.BytesIO(img_byte_arr))])
        return response.text
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def extract_car_details(text):
    details = {
        'brand': None,
        'model': None,
        'year': None,
        'type': None
    }
    
    # Extract brand
    brand_match = re.search(r'Make:\s*([^\n]+)', text, re.IGNORECASE)
    if brand_match:
        details['brand'] = brand_match.group(1).strip()
    
    # Extract model
    model_match = re.search(r'Model:\s*([^\n]+)', text, re.IGNORECASE)
    if model_match:
        details['model'] = model_match.group(1).strip()
    
    # Extract year
    year_match = re.search(r'Year:\s*(\d{4})', text, re.IGNORECASE)
    if year_match:
        details['year'] = int(year_match.group(1))
    else:
        # Try to find year in text
        year_match = re.search(r'(\d{4})', text)
        if year_match:
            details['year'] = int(year_match.group(1))
    
    # Extract type
    type_match = re.search(r'Type:\s*([^\n]+)', text, re.IGNORECASE)
    if type_match:
        details['type'] = type_match.group(1).strip()
    
    return details 