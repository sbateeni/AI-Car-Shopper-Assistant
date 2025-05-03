import streamlit as st
import google.generativeai as genai
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.0-flash-001')

def compare_cars(car1_specs, car2_specs):
    try:
        prompt = f"""
        Compare these two cars and provide a detailed analysis:
        
        Car 1:
        {json.dumps(car1_specs, indent=2)}
        
        Car 2:
        {json.dumps(car2_specs, indent=2)}
        
        Provide the comparison in the following format:
        1. Overall Comparison
        2. Performance Comparison
        3. Technical Specifications
        4. Pros and Cons of each car
        5. Recommendation based on different use cases
        
        Format the response in a clear, structured way with bullet points and clear sections.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error comparing cars: {str(e)}")
        return None

def main():
    st.title("🚗 Car Comparison Tool")
    st.write("Compare different cars based on their specifications")
    
    # Create two columns for car inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Car 1")
        car1_brand = st.text_input("Brand", key="car1_brand")
        car1_model = st.text_input("Model", key="car1_model")
        car1_year = st.number_input("Year", min_value=1900, max_value=2024, value=2023, key="car1_year")
        
    with col2:
        st.subheader("Car 2")
        car2_brand = st.text_input("Brand", key="car2_brand")
        car2_model = st.text_input("Model", key="car2_model")
        car2_year = st.number_input("Year", min_value=1900, max_value=2024, value=2023, key="car2_year")
    
    # Get specifications for both cars
    if st.button("Compare Cars"):
        with st.spinner("Analyzing cars..."):
            # Get specifications for car 1
            prompt1 = f"""
            Please provide detailed specifications for a {car1_year} {car1_brand} {car1_model}.
            Include:
            1. Brand
            2. Model
            3. Year
            4. Fuel consumption (liters/100km)
            5. Engine size (cc)
            6. Number of cylinders
            7. Transmission type
            8. Fuel type
            9. Horsepower
            10. Torque (Nm)
            11. Top speed (km/h)
            12. Acceleration 0-100 km/h (seconds)
            13. Price range (USD)
            14. Safety features
            15. Comfort features
            16. Technology features
            
            Format the response as a JSON object.
            """
            
            response1 = model.generate_content(prompt1)
            car1_specs = json.loads(response1.text)
            
            # Get specifications for car 2
            prompt2 = f"""
            Please provide detailed specifications for a {car2_year} {car2_brand} {car2_model}.
            Include:
            1. Brand
            2. Model
            3. Year
            4. Fuel consumption (liters/100km)
            5. Engine size (cc)
            6. Number of cylinders
            7. Transmission type
            8. Fuel type
            9. Horsepower
            10. Torque (Nm)
            11. Top speed (km/h)
            12. Acceleration 0-100 km/h (seconds)
            13. Price range (USD)
            14. Safety features
            15. Comfort features
            16. Technology features
            
            Format the response as a JSON object.
            """
            
            response2 = model.generate_content(prompt2)
            car2_specs = json.loads(response2.text)
            
            # Compare the cars
            comparison = compare_cars(car1_specs, car2_specs)
            
            if comparison:
                st.success("Comparison complete!")
                
                # Display specifications side by side
                st.subheader("Specifications Comparison")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{car1_brand} {car1_model} ({car1_year})**")
                    st.json(car1_specs)
                
                with col2:
                    st.write(f"**{car2_brand} {car2_model} ({car2_year})**")
                    st.json(car2_specs)
                
                # Display detailed comparison
                st.subheader("Detailed Comparison")
                st.markdown(comparison)
            else:
                st.error("Failed to compare cars")

if __name__ == "__main__":
    main() 