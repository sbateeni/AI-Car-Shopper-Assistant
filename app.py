import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro-vision')

# Set page configuration
st.set_page_config(
    page_title="Car Type Detector",
    page_icon="🚗",
    layout="centered"
)

# Title and description
st.title("🚗 Car Type Detector")
st.write("Upload an image or use your camera to detect the type of car")

# Function to process image with Gemini API
def detect_car(image):
    try:
        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Prepare the prompt
        prompt = """
        Analyze this car image and provide the following information:
        1. Make (brand)
        2. Model
        3. Year (if possible to determine)
        4. Type of vehicle (SUV, Sedan, Hatchback, etc.)
        
        Format your response as a clear, concise description.
        """
        
        # Get response from Gemini
        response = model.generate_content([prompt, Image.open(io.BytesIO(img_byte_arr))])
        return response.text
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# Create two columns for upload and camera options
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

with col2:
    st.subheader("Use Camera")
    camera_image = st.camera_input("Take a photo")

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
    if st.button("Detect Car Type"):
        with st.spinner("Analyzing image..."):
            result = detect_car(image)
            
            if result:
                st.success("Analysis complete!")
                # Display results
                st.subheader("Detection Results")
                st.write(result)
            else:
                st.error("Failed to process the image")

# Add instructions
st.markdown("""
### Instructions:
1. Either upload an image or use your camera to take a photo of a car
2. Click the 'Detect Car Type' button
3. Wait for the AI to analyze the image
4. View the results showing the detected car type and other details
""") 