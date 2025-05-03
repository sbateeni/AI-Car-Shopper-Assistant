import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=api_key)
vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
text_model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Set page configuration
st.set_page_config(
    page_title="Car Type Detector",
    page_icon="🚗",
    layout="centered"
)

# Title and description
st.title("🚗 Car Type Detector")
st.write("Upload an image or use your camera to detect the type of car and get detailed specifications")

# Function to process image with Gemini Vision API
def detect_car(image):
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
        st.error(f"Error processing image: {str(e)}")
        return None

# Function to extract car details from text
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

# Function to get vehicle specifications
def get_vehicle_specs(brand: str, model: str, year: int):
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
            "acceleration": float
        }}
        
        Important:
        - Return ONLY the JSON object, no additional text
        - Use exact values for brand, model, and year as provided
        - Ensure all numeric values are actual numbers, not strings
        - If any value is unknown, use null
        """
        
        response = text_model.generate_content(prompt)
        
        if not response or not response.text:
            st.error("Received empty response from Gemini")
            return None
        
        try:
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
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse JSON: {e}")
            return None
    except Exception as e:
        st.error(f"Error getting vehicle specs: {e}")
        return None

# Create two columns for upload and camera options
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

with col2:
    st.subheader("Use Camera")
    camera_image = st.camera_input("Take a photo")

# Process the image
if uploaded_file or camera_image:
    # Get the image from either source
    if uploaded_file:
        image = Image.open(uploaded_file)
    else:
        image = Image.open(camera_image)
    
    # Display the image
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Process button
    if st.button("Detect Car Type"):
        with st.spinner("Analyzing image..."):
            # First, detect the car from the image
            car_info = detect_car(image)
            
            if car_info:
                st.success("Car detection complete!")
                st.subheader("Car Information")
                st.write(car_info)
                
                # Extract car details
                car_details = extract_car_details(car_info)
                
                if car_details['brand'] and car_details['model']:
                    # Get detailed specifications
                    with st.spinner("Getting detailed specifications..."):
                        specs = get_vehicle_specs(
                            car_details['brand'],
                            car_details['model'],
                            car_details['year'] or 2023  # Use current year if year not detected
                        )
                        
                        if specs:
                            st.subheader("Detailed Specifications")
                            
                            # Create a more readable display of specifications
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Basic Information**")
                                st.write(f"Brand: {specs['brand']}")
                                st.write(f"Model: {specs['model']}")
                                st.write(f"Year: {specs['year']}")
                                st.write(f"Type: {car_details['type'] or 'Unknown'}")
                                
                            with col2:
                                st.write("**Performance**")
                                st.write(f"Engine: {specs['engine_size']}cc, {specs['cylinders']} cylinders")
                                st.write(f"Horsepower: {specs['horsepower']} HP")
                                st.write(f"Torque: {specs['torque']} Nm")
                                st.write(f"Top Speed: {specs['top_speed']} km/h")
                                st.write(f"0-100 km/h: {specs['acceleration']} seconds")
                            
                            st.write("**Technical Details**")
                            st.write(f"Transmission: {specs['transmission']}")
                            st.write(f"Fuel Type: {specs['fuel_type']}")
                            st.write(f"Fuel Consumption: {specs['fuel_consumption']} L/100km")
                else:
                    st.warning("Could not extract enough information for detailed specifications")
            else:
                st.error("Failed to process the image")

# Add instructions
st.markdown("""
### Instructions:
1. Either upload an image or use your camera to take a photo of a car
2. Click the 'Detect Car Type' button
3. Wait for the AI to analyze the image and provide:
   - Basic car information (make, model, year, type)
   - Detailed specifications (performance, technical details)
""") 