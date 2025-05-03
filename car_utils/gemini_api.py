import google.generativeai as genai
import streamlit as st
from .config import GEMINI_SETTINGS
import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env
load_dotenv()

def configure_api():
    """تكوين مفتاح API باستخدام ملف .env"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        return True
    else:
        st.error("⚠️ لم يتم العثور على مفتاح API. يرجى إضافة مفتاح API في ملف .env")
        return False

def call_gemini_vision(image_base64, text_prompt):
    """
    تستدعي Gemini API لتحليل الصورة والنص.
    """
    try:
        model = genai.GenerativeModel(GEMINI_SETTINGS["vision_model"])
        image_parts = [{"mime_type": "image/png", "data": image_base64}]
        response = model.generate_content([text_prompt, image_parts])
        return response.text
    except Exception as e:
        st.error(f"خطأ في استدعاء Gemini API: {e}")
        return "عذراً، حدث خطأ في تحليل الصورة. يرجى المحاولة مرة أخرى."

def call_gemini_text(text_prompt):
    """
    تستدعي Gemini API لمعالجة النصوص.
    """
    try:
        model = genai.GenerativeModel(GEMINI_SETTINGS["text_model"])
        response = model.generate_content(text_prompt)
        return response.text
    except Exception as e:
        st.error(f"خطأ في استدعاء Gemini API: {e}")
        return "عذراً، حدث خطأ في معالجة النص. يرجى المحاولة مرة أخرى." 