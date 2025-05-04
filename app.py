import io
import streamlit as st
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import os
import json
import re
from src.database import save_car, get_all_cars
from src.car_data import get_car_brands, get_car_models, get_car_types, get_car_data_from_brand

# Load environment variables
load_dotenv()

# Initialize session states
if 'language' not in st.session_state:
    st.session_state.language = 'English'

if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('GEMINI_API_KEY', '')

# Language selection
selected_language = st.sidebar.selectbox(
    "Select Language / اختر اللغة",
    options=['English', 'Arabic'],
    index=0 if st.session_state.language == 'English' else 1
)

if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.rerun()

# API Key input
st.sidebar.subheader("API Key Settings / إعدادات مفتاح API")

# Add link to API key page
st.sidebar.markdown(
    f'<a href="https://makersuite.google.com/app/apikey" target="_blank" style="text-decoration: none;">'
    f'<button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: 100%;">'
    f'Get API Key / الحصول على مفتاح API'
    f'</button></a>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")  # Add a separator

api_key = st.sidebar.text_input(
    "Enter your Gemini API Key / أدخل مفتاح API الخاص بك",
    value=st.session_state.api_key,
    type="password"
)

# Create two columns for save and delete buttons
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("Save API Key / حفظ المفتاح"):
        # Save to .env file
        with open('.env', 'w') as f:
            f.write(f'GEMINI_API_KEY={api_key}')
        
        # Update session state
        st.session_state.api_key = api_key
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        st.sidebar.success("API Key saved successfully / تم حفظ المفتاح بنجاح")

with col2:
    if st.button("Delete API Key / حذف المفتاح"):
        # Delete from .env file
        with open('.env', 'w') as f:
            f.write('GEMINI_API_KEY=')
        
        # Update session state
        st.session_state.api_key = ''
        
        # Clear API configuration
        genai.configure(api_key='')
        
        st.sidebar.success("API Key deleted successfully / تم حذف المفتاح بنجاح")
        st.rerun()

# Configure Gemini API
if st.session_state.api_key:
    genai.configure(api_key=st.session_state.api_key)
else:
    st.warning("Please enter your Gemini API Key / الرجاء إدخال مفتاح API الخاص بك")

# Initialize models
vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
text_model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Get language-specific texts
texts = {
    "English": {
        "title": "Car Type Detector",
        "description": "Upload an image to detect car type and get detailed specifications",
        "upload": "Upload an image",
        "camera": "Use camera",
        "detect": "Detect Car Type",
        "compare": "Compare with Another Car",
        "identify": "Identify Car",
        "specs": "Vehicle Specifications",
        "basic_info": "Basic Information",
        "performance": "Performance",
        "technical": "Technical Specifications",
        "features": "Features",
        "price": "Price Range",
        "safety": "Safety Features",
        "comfort": "Comfort Features",
        "tech": "Technology Features",
        "no_image": "Please upload an image first"
    },
    "Arabic": {
        "title": "كاشف نوع السيارة",
        "description": "قم برفع صورة للكشف عن نوع السيارة والحصول على مواصفات تفصيلية",
        "upload": "رفع صورة",
        "camera": "استخدام الكاميرا",
        "detect": "كشف نوع السيارة",
        "compare": "مقارنة مع سيارة أخرى",
        "identify": "تحديد السيارة",
        "specs": "مواصفات المركبة",
        "basic_info": "المعلومات الأساسية",
        "performance": "الأداء",
        "technical": "المواصفات الفنية",
        "features": "المميزات",
        "price": "نطاق السعر",
        "safety": "مميزات الأمان",
        "comfort": "مميزات الراحة",
        "tech": "المميزات التكنولوجية",
        "no_image": "الرجاء رفع صورة أولاً"
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

# Add manual car input section
st.subheader("إضافة سيارة يدوياً / Add Car Manually")

col1, col2, col3 = st.columns(3)
with col1:
    brand = st.text_input("الشركة المصنعة / Brand")
with col2:
    model = st.text_input("الموديل / Model")
with col3:
    year = st.text_input("السنة / Year")

car_type = st.selectbox(
    "الفئة / Type",
    ["SUV", "Sedan", "Hatchback", "Coupe", "Sports Car", "Pickup", "Van", "Wagon", "Convertible", "Crossover", "Luxury", "Electric", "Hybrid", "Other"]
)

st.markdown("---")  # Add a separator

# Create two columns for upload and camera options
col1, col2 = st.columns(2)

with col1:
    st.subheader(texts[st.session_state.language]["upload"])
    uploaded_file = st.file_uploader(
        label="اختر صورة سيارة / Choose a car image",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible"
    )

# Process button - always visible
if st.button(texts[st.session_state.language]["detect"], label_visibility="visible"):
    if uploaded_file:
        # Process image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        with st.spinner("Processing image..."):
            car_details, specs = process_car(image, st.session_state.language)
    elif brand and model and year:
        # Process manual input
        with st.spinner("Processing car details..."):
            # Create car details from manual input
            car_details = {
                'brand': brand,
                'model': model,
                'year': year,
                'type': car_type
            }
            
            # Get specifications using Gemini
            specs_prompt = f"""قم بإنشاء مواصفات تفصيلية لسيارة {year} {brand} {model} بتنسيق JSON:
            {{
                "basic_info": {{
                    "brand": "{brand}",
                    "model": "{model}",
                    "year": "{year}",
                    "type": "{car_type}"
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
    else:
        st.warning("يرجى إما رفع صورة أو إدخال بيانات السيارة / Please either upload an image or enter car details")
        st.stop()
    
    if car_details and specs:
        # Store car details
        car_data = {
            'details': car_details,
            'specs': specs,
            'image': image if uploaded_file else None
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
        if st.button(texts[st.session_state.language]["compare"], label_visibility="visible"):
            st.switch_page("pages/compare.py")
        
        # Add identify button
        if st.button(texts[st.session_state.language]["identify"], label_visibility="visible"):
            st.switch_page("pages/identify.py") 