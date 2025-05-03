import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize model
model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Language selection
language = st.sidebar.selectbox(
    "Select Language / اختر اللغة",
    ["English", "Arabic"]
)

# Get language-specific texts
texts = {
    "English": {
        "title": "Car Comparison",
        "description": "Compare two cars based on their specifications",
        "car1": "First Car",
        "car2": "Second Car",
        "brand": "Brand",
        "model": "Model",
        "year": "Year",
        "compare": "Compare Cars",
        "overall": "Overall Comparison",
        "performance": "Performance Comparison",
        "technical": "Technical Specifications",
        "pros_cons": "Pros and Cons",
        "recommendation": "Recommendation"
    },
    "Arabic": {
        "title": "مقارنة السيارات",
        "description": "قارن بين سيارتين بناءً على مواصفاتهما",
        "car1": "السيارة الأولى",
        "car2": "السيارة الثانية",
        "brand": "الماركة",
        "model": "الموديل",
        "year": "السنة",
        "compare": "مقارنة السيارات",
        "overall": "مقارنة عامة",
        "performance": "مقارنة الأداء",
        "technical": "المواصفات الفنية",
        "pros_cons": "الإيجابيات والسلبيات",
        "recommendation": "التوصية"
    }
}

# Main title and description
st.title(texts[language]["title"])
st.write(texts[language]["description"])

# Create two columns for car inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader(texts[language]["car1"])
    car1_brand = st.text_input(f"{texts[language]['brand']} 1")
    car1_model = st.text_input(f"{texts[language]['model']} 1")
    car1_year = st.text_input(f"{texts[language]['year']} 1")

with col2:
    st.subheader(texts[language]["car2"])
    car2_brand = st.text_input(f"{texts[language]['brand']} 2")
    car2_model = st.text_input(f"{texts[language]['model']} 2")
    car2_year = st.text_input(f"{texts[language]['year']} 2")

# Compare button
if st.button(texts[language]["compare"]):
    if car1_brand and car1_model and car1_year and car2_brand and car2_model and car2_year:
        try:
            # Get specifications for both cars
            prompt = f"""Compare the following two cars and provide a detailed analysis:
            
            Car 1: {car1_year} {car1_brand} {car1_model}
            Car 2: {car2_year} {car2_brand} {car2_model}
            
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
                st.write(f"**{car1_brand} {car1_model} Pros:**")
                for pro in comparison["pros_and_cons"]["car1_pros"]:
                    st.write(f"✅ {pro}")
                
                st.write(f"**{car1_brand} {car1_model} Cons:**")
                for con in comparison["pros_and_cons"]["car1_cons"]:
                    st.write(f"❌ {con}")
            
            with col2:
                st.write(f"**{car2_brand} {car2_model} Pros:**")
                for pro in comparison["pros_and_cons"]["car2_pros"]:
                    st.write(f"✅ {pro}")
                
                st.write(f"**{car2_brand} {car2_model} Cons:**")
                for con in comparison["pros_and_cons"]["car2_cons"]:
                    st.write(f"❌ {con}")
            
            st.subheader(texts[language]["recommendation"])
            st.write(comparison["recommendation"])
            
        except Exception as e:
            st.error(f"Error comparing cars: {str(e)}")
    else:
        st.error("Please fill in all fields for both cars") 