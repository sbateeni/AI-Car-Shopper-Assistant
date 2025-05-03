import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

def initialize_models():
    """Initialize Gemini models"""
    # Load environment variables
    load_dotenv()
    
    # Configure Gemini API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    
    # Initialize models
    vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
    text_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
    
    return vision_model, text_model

def load_config():
    """Load application configuration"""
    # Load environment variables
    load_dotenv()
    
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Please set your GEMINI_API_KEY in the .env file")
        st.stop()
    
    genai.configure(api_key=api_key)
    
    # Initialize models
    vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
    text_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
    
    # Set page configuration
    st.set_page_config(
        page_title="Car Type Detector",
        page_icon="🚗",
        layout="centered"
    )
    
    return vision_model, text_model 