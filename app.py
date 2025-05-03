import io
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize models
vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
text_model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Language selection
selected_language = st.selectbox(
    "Select Language / اختر اللغة",
    options=['English', 'Arabic'],
    index=0 if st.session_state.language == 'English' else 1
)

if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.rerun()

# Get language-specific texts
texts = {
    "English": {
        "title": "Car Type Detector",
        "description": "Upload an image or use your camera to detect car type and get detailed specifications",
        "upload": "Upload an image",
        "camera": "Use camera",
        "detect": "Detect Car Type",
        "compare": "Compare with Another Car",
        "specs": "Vehicle Specifications",
        "basic_info": "Basic Information",
        "performance": "Performance",
        "technical": "Technical Specifications",
        "features": "Features",
        "price": "Price Range",
        "safety": "Safety Features",
        "comfort": "Comfort Features",
        "tech": "Technology Features"
    },
    "Arabic": {
        "title": "كاشف نوع السيارة",
        "description": "قم برفع صورة أو استخدم الكاميرا للكشف عن نوع السيارة والحصول على مواصفات تفصيلية",
        "upload": "رفع صورة",
        "camera": "استخدام الكاميرا",
        "detect": "كشف نوع السيارة",
        "compare": "مقارنة مع سيارة أخرى",
        "specs": "مواصفات المركبة",
        "basic_info": "المعلومات الأساسية",
        "performance": "الأداء",
        "technical": "المواصفات الفنية",
        "features": "المميزات",
        "price": "نطاق السعر",
        "safety": "مميزات الأمان",
        "comfort": "مميزات الراحة",
        "tech": "المميزات التكنولوجية"
    }
}

# Title and description
st.title(texts[st.session_state.language]["title"])
st.write(texts[st.session_state.language]["description"])

# Create two columns for upload and camera options
col1, col2 = st.columns(2)

with col1:
    st.subheader(texts[st.session_state.language]["upload"])
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

with col2:
    st.subheader(texts[st.session_state.language]["camera"])
    camera_image = st.camera_input("")

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
    if st.button(texts[st.session_state.language]["detect"]):
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Detect car details
            response = vision_model.generate_content([
                """Analyze this car image and provide the following information in JSON format:
                {
                    "brand": "car brand",
                    "model": "car model",
                    "year": "year of manufacture",
                    "type": "car type (SUV, Sedan, etc.)"
                }
                Only return the JSON object, nothing else. Do not include any text before or after the JSON.""",
                {"mime_type": "image/jpeg", "data": img_byte_arr}
            ])
            
            # Extract car details from response
            response_text = response.text.strip()
            car_details = json.loads(response_text)
            
            # Get detailed specifications
            specs_prompt = f"""Generate detailed specifications for a {car_details['year']} {car_details['brand']} {car_details['model']} in JSON format:
            {{
                "basic_info": {{
                    "brand": "string",
                    "model": "string",
                    "year": "number",
                    "type": "string"
                }},
                "performance": {{
                    "fuel_consumption": "string",
                    "engine_size": "string",
                    "cylinders": "number",
                    "transmission": "string",
                    "fuel_type": "string",
                    "horsepower": "number",
                    "torque": "string",
                    "top_speed": "string",
                    "acceleration": "string"
                }},
                "technical_specs": {{
                    "length": "string",
                    "width": "string",
                    "height": "string",
                    "wheelbase": "string",
                    "weight": "string",
                    "seating_capacity": "number",
                    "trunk_capacity": "string"
                }},
                "features": {{
                    "price_range": "string",
                    "safety_features": ["string"],
                    "comfort_features": ["string"],
                    "technology_features": ["string"]
                }}
            }}
            Only return the JSON object, nothing else. Do not include any text before or after the JSON."""
            
            response = text_model.generate_content(specs_prompt)
            specs = json.loads(response.text.strip())
            
            # Store car details in session state for comparison
            st.session_state.current_car = {
                'details': car_details,
                'specs': specs,
                'image': image
            }
            
            # Display specifications
            st.subheader(texts[st.session_state.language]["specs"])
            
            # Basic Information
            st.subheader(texts[st.session_state.language]["basic_info"])
            basic_info = specs["basic_info"]
            st.write(f"**Brand:** {basic_info['brand']}")
            st.write(f"**Model:** {basic_info['model']}")
            st.write(f"**Year:** {basic_info['year']}")
            st.write(f"**Type:** {basic_info['type']}")
            
            # Performance
            st.subheader(texts[st.session_state.language]["performance"])
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
            st.subheader(texts[st.session_state.language]["technical"])
            tech_specs = specs["technical_specs"]
            st.write(f"**Length:** {tech_specs['length']}")
            st.write(f"**Width:** {tech_specs['width']}")
            st.write(f"**Height:** {tech_specs['height']}")
            st.write(f"**Wheelbase:** {tech_specs['wheelbase']}")
            st.write(f"**Weight:** {tech_specs['weight']}")
            st.write(f"**Seating Capacity:** {tech_specs['seating_capacity']}")
            st.write(f"**Trunk Capacity:** {tech_specs['trunk_capacity']}")
            
            # Features
            st.subheader(texts[st.session_state.language]["features"])
            features = specs["features"]
            st.write(f"**{texts[st.session_state.language]['price']}:** {features['price_range']}")
            
            st.write(f"**{texts[st.session_state.language]['safety']}:**")
            for feature in features["safety_features"]:
                st.write(f"- {feature}")
                
            st.write(f"**{texts[st.session_state.language]['comfort']}:**")
            for feature in features["comfort_features"]:
                st.write(f"- {feature}")
                
            st.write(f"**{texts[st.session_state.language]['tech']}:**")
            for feature in features["technology_features"]:
                st.write(f"- {feature}")
                
            # Add comparison button
            if st.button(texts[st.session_state.language]["compare"]):
                st.switch_page("pages/compare.py")
                
        except Exception as e:
            st.error(f"Error processing image: {str(e)}") 