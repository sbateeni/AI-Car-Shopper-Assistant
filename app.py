import io
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os
import json
import re
from src.database import save_car, get_all_cars

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
        "tech": "Technology Features",
        "identify": "Identify Car"
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
        "tech": "المميزات التكنولوجية",
        "identify": "تحديد السيارة"
    }
}

def clean_json_string(json_str):
    # Remove any text before or after the JSON object
    json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    
    # Remove any markdown formatting
    json_str = json_str.replace('```json', '').replace('```', '')
    
    # Remove any whitespace at the beginning and end
    json_str = json_str.strip()
    
    return json_str

def process_car(image, language):
    try:
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Detect car details
        detection_prompt = """قم بتحليل صورة السيارة وقدم المعلومات التالية بتنسيق JSON:
        {
            "brand": "ماركة السيارة",
            "model": "موديل السيارة",
            "year": "سنة التصنيع",
            "type": "نوع السيارة (SUV, Sedan, إلخ)"
        }
        قم بإرجاع كائن JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن."""
        
        response = vision_model.generate_content([
            detection_prompt,
            {"mime_type": "image/jpeg", "data": img_byte_arr}
        ])
        
        # Clean and parse the response
        response_text = clean_json_string(response.text)
        car_details = json.loads(response_text)
        
        # Get detailed specifications
        specs_prompt = f"""قم بإنشاء مواصفات تفصيلية لسيارة {car_details['year']} {car_details['brand']} {car_details['model']} بتنسيق JSON:
        {{
            "basic_info": {{
                "brand": "ماركة السيارة",
                "model": "موديل السيارة",
                "year": "سنة التصنيع",
                "type": "نوع السيارة"
            }},
            "performance": {{
                "fuel_consumption": "استهلاك الوقود",
                "engine_size": "حجم المحرك",
                "cylinders": "عدد الأسطوانات",
                "transmission": "نوع ناقل الحركة",
                "fuel_type": "نوع الوقود",
                "horsepower": "قوة المحرك",
                "torque": "عزم الدوران",
                "top_speed": "السرعة القصوى",
                "acceleration": "التسارع"
            }},
            "technical_specs": {{
                "length": "الطول",
                "width": "العرض",
                "height": "الارتفاع",
                "wheelbase": "قاعدة العجلات",
                "weight": "الوزن",
                "seating_capacity": "سعة المقاعد",
                "trunk_capacity": "سعة الصندوق"
            }},
            "features": {{
                "price_range": "نطاق السعر",
                "safety_features": ["مميزات الأمان"],
                "comfort_features": ["مميزات الراحة"],
                "technology_features": ["المميزات التكنولوجية"]
            }}
        }}
        يجب أن تكون جميع الإجابات باللغة العربية.
        قم بإرجاع كائن JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن."""
        
        response = text_model.generate_content(specs_prompt)
        specs_text = clean_json_string(response.text)
        specs = json.loads(specs_text)
        
        return car_details, specs
        
    except Exception as e:
        st.error(f"خطأ في معالجة الصورة: {str(e)}")
        return None, None

# Title and description
st.title(texts[st.session_state.language]["title"])
st.write(texts[st.session_state.language]["description"])

# Create two columns for upload and camera options
col1, col2 = st.columns(2)

with col1:
    st.subheader(texts[st.session_state.language]["upload"])
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

# Process the image
if uploaded_file:
    # Get the image
    image = Image.open(uploaded_file)
    
    # Display the image
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Process button
    if st.button(texts[st.session_state.language]["detect"]):
        with st.spinner("Processing image..."):
            car_details, specs = process_car(image, st.session_state.language)
            
            if car_details and specs:
                # Store car details
                car_data = {
                    'details': car_details,
                    'specs': specs,
                    'image': image
                }
                
                # Save to database
                save_car(car_data)
                
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
                
                # Add identify button
                if st.button(texts[st.session_state.language]["identify"]):
                    st.switch_page("pages/identify.py")
    else:
        st.warning(texts[st.session_state.language]["no_image"]) 