import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_gemini():
    """
    Configure Gemini API with the current API key
    """
    api_key = st.session_state.get('api_key', os.getenv('GEMINI_API_KEY', ''))
    if api_key:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('models/gemini-2.0-flash-001')
    return None

def get_car_models(brand):
    """
    Get all car models for a specific brand using Gemini API
    """
    try:
        model = configure_gemini()
        if not model:
            st.error("يرجى إدخال مفتاح Gemini API في الصفحة الرئيسية أولاً.")
            return []

        prompt = f"""قم بإرجاع جميع موديلات سيارات {brand} بتنسيق JSON:
        {{
            "models": [
                {{
                    "name": "اسم الموديل",
                    "years": ["سنوات الإنتاج"],
                    "type": "نوع السيارة"
                }}
            ]
        }}
        
        يجب أن تكون جميع الإجابات باللغة العربية.
        قم بإرجاع كائن JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse the response
        data = json.loads(response_text)
        return data['models']
        
    except Exception as e:
        st.error(f"خطأ في جلب موديلات السيارات: {str(e)}")
        return []

def get_car_types():
    """
    Get all car types
    """
    return [
        "SUV",
        "Sedan",
        "Hatchback",
        "Coupe",
        "Sports Car",
        "Pickup",
        "Van",
        "Wagon",
        "Convertible",
        "Crossover",
        "Luxury",
        "Electric",
        "Hybrid",
        "Other"
    ]

def get_car_brands():
    """
    Get all car brands
    """
    try:
        model = configure_gemini()
        if not model:
            st.error("يرجى إدخال مفتاح Gemini API في الصفحة الرئيسية أولاً.")
            return []

        prompt = """قم بإرجاع قائمة بجميع شركات تصنيع السيارات المعروفة بتنسيق JSON:
        {
            "brands": [
                {
                    "name": "اسم الشركة",
                    "country": "بلد المنشأ"
                }
            ]
        }
        
        يجب أن تكون جميع الإجابات باللغة العربية.
        قم بإرجاع كائن JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse the response
        data = json.loads(response_text)
        return data['brands']
        
    except Exception as e:
        st.error(f"خطأ في جلب شركات السيارات: {str(e)}")
        return []

def get_car_data_from_brand(brand):
    """
    Get detailed car data for a manually entered brand using Gemini API
    """
    try:
        model = configure_gemini()
        if not model:
            st.error("يرجى إدخال مفتاح Gemini API في الصفحة الرئيسية أولاً.")
            return None

        prompt = f"""قم بإرجاع معلومات تفصيلية عن سيارات {brand} بتنسيق JSON:
        {{
            "brand_info": {{
                "name": "اسم الشركة",
                "country": "بلد المنشأ",
                "founded_year": "سنة التأسيس",
                "description": "وصف مختصر عن الشركة"
            }},
            "popular_models": [
                {{
                    "name": "اسم الموديل",
                    "years": ["سنوات الإنتاج"],
                    "type": "نوع السيارة",
                    "description": "وصف مختصر للموديل"
                }}
            ],
            "car_types": ["أنواع السيارات التي تنتجها الشركة"]
        }}
        
        يجب أن تكون جميع الإجابات باللغة العربية.
        قم بإرجاع كائن JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse the response
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        st.error(f"خطأ في جلب بيانات السيارة: {str(e)}")
        return None 