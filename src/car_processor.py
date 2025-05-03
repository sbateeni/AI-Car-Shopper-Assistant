import json
import streamlit as st
from PIL import Image
import io
import re

def clean_json_string(json_str):
    """Clean and fix common JSON formatting issues"""
    # Remove any leading/trailing whitespace and newlines
    json_str = json_str.strip()
    
    # Remove markdown code block if present
    json_str = re.sub(r'^```json\s*|\s*```$', '', json_str)
    
    # Fix common formatting issues
    json_str = re.sub(r'\\n', '', json_str)  # Remove \n
    json_str = re.sub(r'\\"', '"', json_str)  # Fix escaped quotes
    json_str = re.sub(r'"{', '{', json_str)  # Fix extra quotes
    json_str = re.sub(r'}"', '}', json_str)  # Fix extra quotes
    
    # Remove any text before or after the JSON object
    json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
    if json_match:
        json_str = json_match.group()
    
    return json_str

def process_car(image, vision_model, text_model, language):
    """Process car image and get specifications"""
    try:
        # Convert image to bytes if it's not already
        if isinstance(image, Image.Image):
            img_byte_arr = io.BytesIO()
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
        else:
            img_byte_arr = image

        # Get language-specific prompts
        from src.language import get_language_prompts
        prompts = get_language_prompts(language)
        
        # Detect car details
        response = vision_model.generate_content([
            prompts["detection_prompt"],
            {"mime_type": "image/jpeg", "data": img_byte_arr}
        ])
        
        # Extract car details from response
        response_text = response.text.strip()
        st.write("Raw response from vision model:", response_text)  # Debug output
        
        # Clean the response text
        cleaned_text = clean_json_string(response_text)
        
        try:
            # Try to parse the cleaned response
            car_details = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            st.error(f"Error parsing car details JSON: {str(e)}")
            st.error(f"Cleaned response: {cleaned_text}")
            return None, None
        
        # Validate car details
        required_fields = ["brand", "model", "year", "type"]
        if not all(field in car_details for field in required_fields):
            st.error("Missing required fields in car details")
            return None, None
        
        # Get detailed specifications
        specs_prompt = prompts["specs_prompt"].format(
            year=car_details["year"],
            brand=car_details["brand"],
            model=car_details["model"]
        )
        
        response = text_model.generate_content(specs_prompt)
        
        # Extract specifications from response
        response_text = response.text.strip()
        st.write("Raw response from text model:", response_text)  # Debug output
        
        # Clean the response text
        cleaned_text = clean_json_string(response_text)
        
        try:
            # Try to parse the cleaned response
            specs = json.loads(cleaned_text)
            
            # Validate specs structure
            required_sections = ["basic_info", "performance", "technical_specs", "features"]
            if not all(section in specs for section in required_sections):
                st.error("Missing required sections in specifications")
                return car_details, None
                
            # Validate basic_info
            required_basic_info = ["brand", "model", "year", "type"]
            if not all(field in specs["basic_info"] for field in required_basic_info):
                st.error("Missing required fields in basic_info")
                return car_details, None
                
        except json.JSONDecodeError as e:
            st.error(f"Error parsing specifications JSON: {str(e)}")
            st.error(f"Cleaned response: {cleaned_text}")
            return car_details, None
        
        return car_details, specs
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

def display_specifications(specs, language):
    """Display car specifications"""
    if not specs:
        return
        
    # Get language-specific texts
    from src.language import get_language_texts
    texts = get_language_texts(language)
    
    st.subheader(texts["specs"])
    
    # Basic Information
    st.subheader(texts["basic_info"])
    basic_info = specs["basic_info"]
    st.write(f"**Brand:** {basic_info['brand']}")
    st.write(f"**Model:** {basic_info['model']}")
    st.write(f"**Year:** {basic_info['year']}")
    st.write(f"**Type:** {basic_info['type']}")
    
    # Performance
    st.subheader(texts["performance"])
    performance = specs["performance"]
    st.write(f"**Fuel Consumption:** {performance['fuel_consumption']}")
    st.write(f"**Engine Size:** {performance['engine_size']}")
    st.write(f"**Cylinders:** {performance['cylinders']}")
    st.write(f"**Transmission:** {performance['transmission']}")
    st.write(f"**Fuel Type:** {performance['fuel_type']}")
    st.write(f"**Horsepower:** {performance['horsepower']}")
    st.write(f"**Torque:** {performance['torque']}")
    st.write(f"**Top Speed:** {performance['top_speed']}")
    st.write(f"**Acceleration:** {performance['acceleration']}")
    
    # Technical Specifications
    st.subheader(texts["technical"])
    tech_specs = specs["technical_specs"]
    st.write(f"**Length:** {tech_specs['length']}")
    st.write(f"**Width:** {tech_specs['width']}")
    st.write(f"**Height:** {tech_specs['height']}")
    st.write(f"**Wheelbase:** {tech_specs['wheelbase']}")
    st.write(f"**Weight:** {tech_specs['weight']}")
    st.write(f"**Seating Capacity:** {tech_specs['seating_capacity']}")
    st.write(f"**Trunk Capacity:** {tech_specs['trunk_capacity']}")
    
    # Features
    st.subheader(texts["features"])
    features = specs["features"]
    st.write(f"**{texts['price']}:** {features['price_range']}")
    
    st.write(f"**{texts['safety']}:**")
    for feature in features["safety_features"]:
        st.write(f"- {feature}")
        
    st.write(f"**{texts['comfort']}:**")
    for feature in features["comfort_features"]:
        st.write(f"- {feature}")
        
    st.write(f"**{texts['tech']}:**")
    for feature in features["technology_features"]:
        st.write(f"- {feature}") 