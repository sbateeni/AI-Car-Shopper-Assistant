import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
from src.car_detection import detect_car, extract_car_details
from src.car_specs import get_vehicle_specs

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=api_key)
vision_model = genai.GenerativeModel('models/gemini-2.0-flash-001')
text_model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Set page configuration
st.set_page_config(
    page_title="Car Type Detector",
    page_icon="🚗",
    layout="centered"
)

# Initialize session state for storing cars
if 'detected_cars' not in st.session_state:
    st.session_state.detected_cars = []
if 'continue_adding' not in st.session_state:
    st.session_state.continue_adding = True

# Title and description
st.title("🚗 Car Type Detector")
st.write("Upload images or use your camera to detect multiple cars and compare them")

# Function to process a single car
def process_car(image):
    try:
        # First, detect the car from the image
        car_info = detect_car(image, vision_model)
        
        if car_info:
            st.success("Car detection complete!")
            st.subheader("Car Information")
            st.write(car_info)
            
            # Extract car details
            car_details = extract_car_details(car_info)
            
            if car_details['brand'] and car_details['model']:
                # Get detailed specifications
                with st.spinner("Getting detailed specifications..."):
                    specs = get_vehicle_specs(
                        car_details['brand'],
                        car_details['model'],
                        car_details['year'] or 2023,  # Use current year if year not detected
                        text_model
                    )
                    
                    if specs:
                        st.subheader("Detailed Specifications")
                        
                        # Create a more readable display of specifications
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Basic Information**")
                            st.write(f"Brand: {specs['brand']}")
                            st.write(f"Model: {specs['model']}")
                            st.write(f"Year: {specs['year']}")
                            st.write(f"Type: {car_details['type'] or 'Unknown'}")
                            
                        with col2:
                            st.write("**Performance**")
                            st.write(f"Engine: {specs['engine_size']}cc, {specs['cylinders']} cylinders")
                            st.write(f"Horsepower: {specs['horsepower']} HP")
                            st.write(f"Torque: {specs['torque']} Nm")
                            st.write(f"Top Speed: {specs['top_speed']} km/h")
                            st.write(f"0-100 km/h: {specs['acceleration']} seconds")
                        
                        st.write("**Technical Details**")
                        st.write(f"Transmission: {specs['transmission']}")
                        st.write(f"Fuel Type: {specs['fuel_type']}")
                        st.write(f"Fuel Consumption: {specs['fuel_consumption']} L/100km")
                        
                        st.write("**Features**")
                        st.write("Safety Features:")
                        for feature in specs['safety_features']:
                            st.write(f"- {feature}")
                        
                        st.write("Comfort Features:")
                        for feature in specs['comfort_features']:
                            st.write(f"- {feature}")
                        
                        st.write("Technology Features:")
                        for feature in specs['technology_features']:
                            st.write(f"- {feature}")
                        
                        # Add car to detected cars list
                        car_data = {
                            'brand': specs['brand'],
                            'model': specs['model'],
                            'year': specs['year'],
                            'specs': specs,
                            'image': image
                        }
                        
                        # Check if car is already in the list
                        car_exists = False
                        for car in st.session_state.detected_cars:
                            if (car['brand'] == car_data['brand'] and 
                                car['model'] == car_data['model'] and 
                                car['year'] == car_data['year']):
                                car_exists = True
                                break
                        
                        if not car_exists:
                            st.session_state.detected_cars.append(car_data)
                            st.success(f"Added {car_data['brand']} {car_data['model']} to comparison list!")
                            
                            # Ask if user wants to add more cars
                            if len(st.session_state.detected_cars) < 2:
                                st.info("You need at least 2 cars to compare. Would you like to add another car?")
                            else:
                                st.info("Would you like to add another car or proceed with comparison?")
                            
                            # Add buttons for next action
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Add Another Car"):
                                    st.session_state.continue_adding = True
                                    st.rerun()
                            with col2:
                                if len(st.session_state.detected_cars) >= 2:
                                    if st.button("Compare Cars Now"):
                                        st.session_state.continue_adding = False
                                        st.switch_page("pages/compare.py")
                        else:
                            st.warning("This car is already in the comparison list")
                            st.info("Would you like to add another car?")
                            if st.button("Add Another Car"):
                                st.session_state.continue_adding = True
                                st.rerun()
                    else:
                        st.warning("Could not extract enough information for detailed specifications")
            else:
                st.warning("Could not extract enough information for detailed specifications")
        else:
            st.error("Failed to process the image")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Main interface
if st.session_state.continue_adding:
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
            process_car(image)

# Display detected cars
if st.session_state.detected_cars:
    st.subheader("Detected Cars")
    for i, car in enumerate(st.session_state.detected_cars):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(car['image'], width=200)
        with col2:
            st.write(f"**{car['brand']} {car['model']} ({car['year']})**")
            st.write(f"Engine: {car['specs']['engine_size']}cc, {car['specs']['cylinders']} cylinders")
            st.write(f"Horsepower: {car['specs']['horsepower']} HP")
            st.write(f"Price Range: {car['specs']['price_range']}")
            
            # Add remove button
            if st.button(f"Remove {car['brand']} {car['model']}", key=f"remove_{i}"):
                st.session_state.detected_cars.pop(i)
                st.rerun()

# Add comparison button if we have at least 2 cars
if len(st.session_state.detected_cars) >= 2 and not st.session_state.continue_adding:
    if st.button("Compare Selected Cars"):
        st.switch_page("pages/compare.py")

# Add instructions
st.markdown("""
### Instructions:
1. Upload images or use your camera to take photos of multiple cars
2. Click 'Detect Car Type' for each car
3. After each detection, you can choose to:
   - Add another car
   - Compare the cars you have (if you have at least 2)
4. View the detected cars in the list below
5. Remove any unwanted cars using the Remove button
6. When ready, click 'Compare Selected Cars' to compare all cars
""") 