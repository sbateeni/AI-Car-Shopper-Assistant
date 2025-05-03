import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re
from src.database import get_all_cars, delete_car

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize model
model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Get all cars from database
detected_cars = get_all_cars()

# Language selection
language = st.sidebar.selectbox(
    "Select Language / اختر اللغة",
    ["English", "Arabic"]
)

# Get language-specific texts
texts = {
    "English": {
        "title": "Car Comparison",
        "description": "Compare cars based on their specifications",
        "detected_cars": "Detected Cars",
        "delete": "Delete",
        "view": "View Details",
        "compare": "Compare Cars",
        "overall": "Overall Comparison",
        "performance": "Performance Comparison",
        "technical": "Technical Specifications",
        "features": "Features",
        "pros_cons": "Pros and Cons",
        "recommendation": "Recommendation",
        "no_cars": "No cars detected. Please go back to the main page and detect some cars first.",
        "select_cars": "Select cars to compare",
        "delete_confirm": "Are you sure you want to delete this car?",
        "select_first": "Select first car",
        "select_second": "Select second car",
        "basic_info": "Basic Information",
        "price": "Price Range",
        "safety": "Safety Features",
        "comfort": "Comfort Features",
        "tech": "Technology Features"
    },
    "Arabic": {
        "title": "مقارنة السيارات",
        "description": "قارن بين السيارات بناءً على مواصفاتها",
        "detected_cars": "السيارات المكتشفة",
        "delete": "حذف",
        "view": "عرض التفاصيل",
        "compare": "مقارنة السيارات",
        "overall": "مقارنة عامة",
        "performance": "مقارنة الأداء",
        "technical": "المواصفات الفنية",
        "features": "المميزات",
        "pros_cons": "الإيجابيات والسلبيات",
        "recommendation": "التوصية",
        "no_cars": "لم يتم اكتشاف أي سيارات. يرجى العودة إلى الصفحة الرئيسية واكتشاف بعض السيارات أولاً.",
        "select_cars": "اختر السيارات للمقارنة",
        "delete_confirm": "هل أنت متأكد من حذف هذه السيارة؟",
        "select_first": "اختر السيارة الأولى",
        "select_second": "اختر السيارة الثانية",
        "basic_info": "المعلومات الأساسية",
        "price": "نطاق السعر",
        "safety": "مميزات الأمان",
        "comfort": "مميزات الراحة",
        "tech": "المميزات التكنولوجية"
    }
}

# Main title and description
st.title(texts[language]["title"])
st.write(texts[language]["description"])

# Display detected cars
st.subheader(texts[language]["detected_cars"])

if not detected_cars:
    st.warning(texts[language]["no_cars"])
    st.stop()

# Display cars in a grid
cols = st.columns(3)
for i, car in enumerate(detected_cars):
    with cols[i % 3]:
        st.image(car['image'], width=200)
        st.write(f"**{car['details']['brand']} {car['details']['model']} ({car['details']['year']})**")
        st.write(f"**Type:** {car['details']['type']}")
        
        # Create two columns for buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # View button
            if st.button(f"{texts[language]['view']} {i+1}", key=f"view_{i}"):
                st.session_state['viewing_car'] = car
                st.rerun()
        
        with col2:
            # Delete button
            if st.button(f"{texts[language]['delete']} {i+1}", key=f"delete_{i}"):
                if st.checkbox(texts[language]["delete_confirm"], key=f"confirm_{i}"):
                    delete_car(car['id'])
                    st.rerun()

# Check if we're viewing a car's details
if 'viewing_car' in st.session_state:
    car = st.session_state['viewing_car']
    
    # Display car details
    st.subheader(f"{car['details']['brand']} {car['details']['model']} ({car['details']['year']})")
    
    # Basic Information
    st.subheader(texts[language]["basic_info"])
    st.write(f"**Brand:** {car['details']['brand']}")
    st.write(f"**Model:** {car['details']['model']}")
    st.write(f"**Year:** {car['details']['year']}")
    st.write(f"**Type:** {car['details']['type']}")
    
    # Performance
    st.subheader(texts[language]["performance"])
    performance = car['specs']['performance']
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
    st.subheader(texts[language]["technical"])
    tech_specs = car['specs']['technical_specs']
    st.write(f"**Length:** {tech_specs['length']}")
    st.write(f"**Width:** {tech_specs['width']}")
    st.write(f"**Height:** {tech_specs['height']}")
    st.write(f"**Wheelbase:** {tech_specs['wheelbase']}")
    st.write(f"**Weight:** {tech_specs['weight']}")
    st.write(f"**Seating Capacity:** {tech_specs['seating_capacity']}")
    st.write(f"**Trunk Capacity:** {tech_specs['trunk_capacity']}")
    
    # Features
    st.subheader(texts[language]["features"])
    features = car['specs']['features']
    st.write(f"**{texts[language]['price']}:** {features['price_range']}")
    
    st.write(f"**{texts[language]['safety']}:**")
    for feature in features["safety_features"]:
        st.write(f"- {feature}")
        
    st.write(f"**{texts[language]['comfort']}:**")
    for feature in features["comfort_features"]:
        st.write(f"- {feature}")
        
    st.write(f"**{texts[language]['tech']}:**")
    for feature in features["technology_features"]:
        st.write(f"- {feature}")
    
    # Back button
    if st.button("Back to Comparison"):
        del st.session_state['viewing_car']
        st.rerun()
    
    st.stop()

# Select cars to compare
st.subheader(texts[language]["select_cars"])
col1, col2 = st.columns(2)

with col1:
    st.write(texts[language]["select_first"])
    car1_index = st.selectbox(
        "",
        range(len(detected_cars)),
        format_func=lambda x: f"{detected_cars[x]['details']['brand']} {detected_cars[x]['details']['model']} ({detected_cars[x]['details']['year']})",
        key="car1_select"
    )

with col2:
    st.write(texts[language]["select_second"])
    car2_index = st.selectbox(
        "",
        range(len(detected_cars)),
        format_func=lambda x: f"{detected_cars[x]['details']['brand']} {detected_cars[x]['details']['model']} ({detected_cars[x]['details']['year']})",
        key="car2_select"
    )

# Compare button
if st.button(texts[language]["compare"]):
    if car1_index != car2_index:
        try:
            car1 = detected_cars[car1_index]
            car2 = detected_cars[car2_index]
            
            # Get specifications for both cars
            prompt = f"""Compare the following two cars and provide a detailed analysis:
            
            Car 1: {car1['details']['year']} {car1['details']['brand']} {car1['details']['model']}
            Car 2: {car2['details']['year']} {car2['details']['brand']} {car2['details']['model']}
            
            Provide the comparison in the following format:
            {{
                "overall_comparison": "string",
                "performance_comparison": "string",
                "technical_comparison": "string",
                "pros_and_cons": {{
                    "car1_pros": ["string"],
                    "car1_cons": ["string"],
                    "car2_pros": ["string"],
                    "car2_cons": ["string"]
                }},
                "recommendation": "string"
            }}
            
            Only return the JSON object, nothing else. Do not include any text before or after the JSON."""
            
            response = model.generate_content(prompt)
            comparison = json.loads(response.text.strip())
            
            # Display comparison results
            st.subheader(texts[language]["overall"])
            st.write(comparison["overall_comparison"])
            
            st.subheader(texts[language]["performance"])
            st.write(comparison["performance_comparison"])
            
            st.subheader(texts[language]["technical"])
            st.write(comparison["technical_comparison"])
            
            st.subheader(texts[language]["pros_cons"])
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**{car1['details']['brand']} {car1['details']['model']} Pros:**")
                for pro in comparison["pros_and_cons"]["car1_pros"]:
                    st.write(f"✅ {pro}")
                
                st.write(f"**{car1['details']['brand']} {car1['details']['model']} Cons:**")
                for con in comparison["pros_and_cons"]["car1_cons"]:
                    st.write(f"❌ {con}")
            
            with col2:
                st.write(f"**{car2['details']['brand']} {car2['details']['model']} Pros:**")
                for pro in comparison["pros_and_cons"]["car2_pros"]:
                    st.write(f"✅ {pro}")
                
                st.write(f"**{car2['details']['brand']} {car2['details']['model']} Cons:**")
                for con in comparison["pros_and_cons"]["car2_cons"]:
                    st.write(f"❌ {con}")
            
            st.subheader(texts[language]["recommendation"])
            st.write(comparison["recommendation"])
            
        except Exception as e:
            st.error(f"Error comparing cars: {str(e)}")
    else:
        st.error("Please select two different cars to compare") 