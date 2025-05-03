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

# Language selection
if 'language' not in st.session_state:
    st.session_state.language = 'English'

# Language texts
texts = {
    'English': {
        'title': "🚗 Car Type Detector",
        'description': "Upload images or use your camera to detect multiple cars and compare them",
        'upload_header': "Upload Image",
        'camera_header': "Use Camera",
        'upload_prompt': "Choose an image...",
        'detect_button': "Detect Car Type",
        'analyzing': "Analyzing image...",
        'detection_complete': "Car detection complete!",
        'car_info': "Car Information",
        'basic_info': "Basic Information",
        'performance': "Performance",
        'technical_details': "Technical Details",
        'features': "Features",
        'safety': "Safety Features",
        'comfort': "Comfort Features",
        'technology': "Technology Features",
        'add_success': "Added {} to comparison list!",
        'already_exists': "This car is already in the comparison list",
        'add_more': "Would you like to add another car?",
        'add_more_or_compare': "Would you like to add another car or proceed with comparison?",
        'need_more': "You need at least 2 cars to compare. Would you like to add another car?",
        'add_another': "Add Another Car",
        'compare_now': "Compare Cars Now",
        'detected_cars': "Detected Cars",
        'remove': "Remove {}",
        'compare_selected': "Compare Selected Cars",
        'instructions': [
            "Upload images or use your camera to take photos of multiple cars",
            "Click 'Detect Car Type' for each car",
            "After each detection, you can choose to:",
            "- Add another car",
            "- Compare the cars you have (if you have at least 2)",
            "View the detected cars in the list below",
            "Remove any unwanted cars using the Remove button",
            "When ready, click 'Compare Selected Cars' to compare all cars"
        ]
    },
    'Arabic': {
        'title': "🚗 كاشف نوع المركبة",
        'description': "قم برفع الصور أو استخدم الكاميرا للكشف عن عدة مركبات ومقارنتها",
        'upload_header': "رفع صورة",
        'camera_header': "استخدام الكاميرا",
        'upload_prompt': "اختر صورة...",
        'detect_button': "كشف نوع المركبة",
        'analyzing': "جاري تحليل الصورة...",
        'detection_complete': "اكتمل الكشف عن المركبة!",
        'car_info': "معلومات المركبة",
        'basic_info': "المعلومات الأساسية",
        'performance': "الأداء",
        'technical_details': "التفاصيل التقنية",
        'features': "المميزات",
        'safety': "مميزات الأمان",
        'comfort': "مميزات الراحة",
        'technology': "المميزات التقنية",
        'add_success': "تمت إضافة {} إلى قائمة المقارنة!",
        'already_exists': "هذه المركبة موجودة بالفعل في قائمة المقارنة",
        'add_more': "هل تريد إضافة مركبة أخرى؟",
        'add_more_or_compare': "هل تريد إضافة مركبة أخرى أو المتابعة للمقارنة؟",
        'need_more': "تحتاج إلى مركبتين على الأقل للمقارنة. هل تريد إضافة مركبة أخرى؟",
        'add_another': "إضافة مركبة أخرى",
        'compare_now': "مقارنة المركبات الآن",
        'detected_cars': "المركبات المكتشفة",
        'remove': "إزالة {}",
        'compare_selected': "مقارنة المركبات المختارة",
        'instructions': [
            "قم برفع الصور أو استخدم الكاميرا لالتقاط صور لعدة مركبات",
            "انقر على 'كشف نوع المركبة' لكل صورة",
            "بعد كل عملية كشف، يمكنك اختيار:",
            "- إضافة مركبة أخرى",
            "- مقارنة المركبات التي لديك (إذا كان لديك مركبتين على الأقل)",
            "عرض المركبات المكتشفة في القائمة أدناه",
            "إزالة أي مركبات غير مرغوب فيها باستخدام زر الإزالة",
            "عندما تكون جاهزاً، انقر على 'مقارنة المركبات المختارة' لمقارنة جميع المركبات"
        ]
    }
}

# Language selection at the top
selected_language = st.selectbox(
    "Select Language / اختر اللغة",
    options=list(texts.keys()),
    index=list(texts.keys()).index(st.session_state.language)
)

if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.rerun()

# Get current language texts
lang = texts[st.session_state.language]

# Initialize session state for storing cars
if 'detected_cars' not in st.session_state:
    st.session_state.detected_cars = []
if 'continue_adding' not in st.session_state:
    st.session_state.continue_adding = True

# Title and description
st.title(lang['title'])
st.write(lang['description'])

# Function to process a single car
def process_car(image):
    try:
        # First, detect the car from the image
        car_info = detect_car(image, vision_model)
        
        if car_info:
            st.success(lang['detection_complete'])
            st.subheader(lang['car_info'])
            st.write(car_info)
            
            # Extract car details
            car_details = extract_car_details(car_info)
            
            if car_details['brand'] and car_details['model']:
                # Get detailed specifications
                with st.spinner(lang['analyzing']):
                    specs = get_vehicle_specs(
                        car_details['brand'],
                        car_details['model'],
                        car_details['year'] or 2023,  # Use current year if year not detected
                        text_model
                    )
                    
                    if specs:
                        st.subheader(lang['technical_details'])
                        
                        # Create a more readable display of specifications
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**{lang['basic_info']}**")
                            st.write(f"Brand: {specs['brand']}")
                            st.write(f"Model: {specs['model']}")
                            st.write(f"Year: {specs['year']}")
                            st.write(f"Type: {car_details['type'] or 'Unknown'}")
                            
                        with col2:
                            st.write(f"**{lang['performance']}**")
                            st.write(f"Engine: {specs['engine_size']}cc, {specs['cylinders']} cylinders")
                            st.write(f"Horsepower: {specs['horsepower']} HP")
                            st.write(f"Torque: {specs['torque']} Nm")
                            st.write(f"Top Speed: {specs['top_speed']} km/h")
                            st.write(f"0-100 km/h: {specs['acceleration']} seconds")
                        
                        st.write(f"**{lang['technical_details']}**")
                        st.write(f"Transmission: {specs['transmission']}")
                        st.write(f"Fuel Type: {specs['fuel_type']}")
                        st.write(f"Fuel Consumption: {specs['fuel_consumption']} L/100km")
                        
                        st.write(f"**{lang['features']}**")
                        st.write(f"{lang['safety']}:")
                        for feature in specs['safety_features']:
                            st.write(f"- {feature}")
                        
                        st.write(f"{lang['comfort']}:")
                        for feature in specs['comfort_features']:
                            st.write(f"- {feature}")
                        
                        st.write(f"{lang['technology']}:")
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
                            st.success(lang['add_success'].format(f"{car_data['brand']} {car_data['model']}"))
                            
                            # Ask if user wants to add more cars
                            if len(st.session_state.detected_cars) < 2:
                                st.info(lang['need_more'])
                            else:
                                st.info(lang['add_more_or_compare'])
                            
                            # Add buttons for next action
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(lang['add_another']):
                                    st.session_state.continue_adding = True
                                    st.rerun()
                            with col2:
                                if len(st.session_state.detected_cars) >= 2:
                                    if st.button(lang['compare_now']):
                                        st.session_state.continue_adding = False
                                        st.switch_page("pages/compare.py")
                        else:
                            st.warning(lang['already_exists'])
                            st.info(lang['add_more'])
                            if st.button(lang['add_another']):
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
        st.subheader(lang['upload_header'])
        uploaded_file = st.file_uploader(lang['upload_prompt'], type=["jpg", "jpeg", "png"])
    
    with col2:
        st.subheader(lang['camera_header'])
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
        if st.button(lang['detect_button']):
            process_car(image)

# Display detected cars
if st.session_state.detected_cars:
    st.subheader(lang['detected_cars'])
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
            if st.button(lang['remove'].format(f"{car['brand']} {car['model']}"), key=f"remove_{i}"):
                st.session_state.detected_cars.pop(i)
                st.rerun()

# Add comparison button if we have at least 2 cars
if len(st.session_state.detected_cars) >= 2 and not st.session_state.continue_adding:
    if st.button(lang['compare_selected']):
        st.switch_page("pages/compare.py")

# Add instructions
st.markdown("""
### Instructions:
{}
""".format("\n".join([f"{i+1}. {instruction}" for i, instruction in enumerate(lang['instructions'])]))) 