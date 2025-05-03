import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize model
model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Initialize session state for detected cars if not exists
if 'detected_cars' not in st.session_state:
    st.session_state.detected_cars = []

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
        "compare": "Compare Cars",
        "overall": "Overall Comparison",
        "performance": "Performance Comparison",
        "technical": "Technical Specifications",
        "pros_cons": "Pros and Cons",
        "recommendation": "Recommendation",
        "no_cars": "No cars detected. Please go back to the main page and detect some cars first.",
        "select_cars": "Select cars to compare",
        "delete_confirm": "Are you sure you want to delete this car?",
        "select_first": "Select first car",
        "select_second": "Select second car"
    },
    "Arabic": {
        "title": "مقارنة السيارات",
        "description": "قارن بين السيارات بناءً على مواصفاتها",
        "detected_cars": "السيارات المكتشفة",
        "delete": "حذف",
        "compare": "مقارنة السيارات",
        "overall": "مقارنة عامة",
        "performance": "مقارنة الأداء",
        "technical": "المواصفات الفنية",
        "pros_cons": "الإيجابيات والسلبيات",
        "recommendation": "التوصية",
        "no_cars": "لم يتم اكتشاف أي سيارات. يرجى العودة إلى الصفحة الرئيسية واكتشاف بعض السيارات أولاً.",
        "select_cars": "اختر السيارات للمقارنة",
        "delete_confirm": "هل أنت متأكد من حذف هذه السيارة؟",
        "select_first": "اختر السيارة الأولى",
        "select_second": "اختر السيارة الثانية"
    }
}

# Main title and description
st.title(texts[language]["title"])
st.write(texts[language]["description"])

# Display detected cars
st.subheader(texts[language]["detected_cars"])

if not st.session_state.detected_cars:
    st.warning(texts[language]["no_cars"])
    st.stop()

# Display cars in a grid
cols = st.columns(3)
for i, car in enumerate(st.session_state.detected_cars):
    with cols[i % 3]:
        st.image(car['image'], width=200)
        st.write(f"**{car['details']['brand']} {car['details']['model']} ({car['details']['year']})**")
        st.write(f"**Type:** {car['details']['type']}")
        
        # Delete button
        if st.button(f"{texts[language]['delete']} {i+1}", key=f"delete_{i}"):
            if st.checkbox(texts[language]["delete_confirm"], key=f"confirm_{i}"):
                st.session_state.detected_cars.pop(i)
                st.rerun()

# Select cars to compare
st.subheader(texts[language]["select_cars"])
col1, col2 = st.columns(2)

with col1:
    st.write(texts[language]["select_first"])
    car1_index = st.selectbox(
        "",
        range(len(st.session_state.detected_cars)),
        format_func=lambda x: f"{st.session_state.detected_cars[x]['details']['brand']} {st.session_state.detected_cars[x]['details']['model']} ({st.session_state.detected_cars[x]['details']['year']})"
    )

with col2:
    st.write(texts[language]["select_second"])
    car2_index = st.selectbox(
        "",
        range(len(st.session_state.detected_cars)),
        format_func=lambda x: f"{st.session_state.detected_cars[x]['details']['brand']} {st.session_state.detected_cars[x]['details']['model']} ({st.session_state.detected_cars[x]['details']['year']})"
    )

# Compare button
if st.button(texts[language]["compare"]):
    if car1_index != car2_index:
        try:
            car1 = st.session_state.detected_cars[car1_index]
            car2 = st.session_state.detected_cars[car2_index]
            
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