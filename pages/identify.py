import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize model
vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Language selection
language = st.sidebar.selectbox(
    "Select Language / اختر اللغة",
    ["English", "Arabic"]
)

# Get language-specific texts
texts = {
    "English": {
        "title": "Car Interior Identifier",
        "description": "Upload an image or use your camera to identify objects inside a car",
        "upload": "Upload an image",
        "camera": "Use camera",
        "identify": "Tell me what this is",
        "no_image": "Please upload an image or use your camera first",
        "error": "Error processing image"
    },
    "Arabic": {
        "title": "معرف محتويات السيارة",
        "description": "قم برفع صورة أو استخدم الكاميرا للتعرف على الأشياء داخل السيارة",
        "upload": "رفع صورة",
        "camera": "استخدام الكاميرا",
        "identify": "اخبرني ما هذا",
        "no_image": "الرجاء رفع صورة أو استخدام الكاميرا أولاً",
        "error": "خطأ في معالجة الصورة"
    }
}

# Main title and description
st.title(texts[language]["title"])
st.write(texts[language]["description"])

# Create two columns for upload and camera options
col1, col2 = st.columns(2)

with col1:
    st.subheader(texts[language]["upload"])
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

with col2:
    st.subheader(texts[language]["camera"])
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
    if st.button(texts[language]["identify"]):
        try:
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            
            # Convert image to RGB if necessary
            if image.mode in ['RGBA', 'P']:
                image = image.convert('RGB')
            
            image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Identify objects in the image
            prompt = """قم بتحليل الصورة ووصف ما تراه باللغة العربية. 
            ركز على الأشياء الموجودة داخل السيارة وقدم وصفاً مفصلاً لكل شيء.
            قم بتحديد:
            1. نوع الشيء أو القطعة
            2. موقعها في السيارة
            3. وظيفتها
            4. أي تفاصيل إضافية مهمة
            
            يجب أن تكون الإجابة باللغة العربية وبشكل منظم وواضح."""
            
            response = vision_model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": img_byte_arr}
            ])
            
            # Display the identification results
            st.subheader("نتيجة التحليل")
            st.write(response.text)
            
        except Exception as e:
            st.error(f"{texts[language]['error']}: {str(e)}")
else:
    st.warning(texts[language]["no_image"]) 