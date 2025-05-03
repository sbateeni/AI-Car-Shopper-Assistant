import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from src.car_comparison import compare_cars

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Title and description
st.title("🚗 Car Comparison Tool")
st.write("Compare multiple cars based on their specifications")

# Get detected cars from session state
detected_cars = st.session_state.get('detected_cars', [])

if not detected_cars:
    st.warning("No cars detected. Please go back to the main page and detect some cars first.")
    st.stop()

# Display cars to compare
st.subheader("Cars to Compare")
for i, car in enumerate(detected_cars):
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(car['image'], width=200)
    with col2:
        st.write(f"**{car['brand']} {car['model']} ({car['year']})**")
        st.write(f"Engine: {car['specs']['engine_size']}cc, {car['specs']['cylinders']} cylinders")
        st.write(f"Horsepower: {car['specs']['horsepower']} HP")
        st.write(f"Price Range: {car['specs']['price_range']}")

# Compare button
if st.button("Compare Cars"):
    with st.spinner("Analyzing cars..."):
        try:
            # Generate pairwise comparisons
            comparisons = []
            for i in range(len(detected_cars)):
                for j in range(i + 1, len(detected_cars)):
                    car1 = detected_cars[i]
                    car2 = detected_cars[j]
                    
                    comparison = compare_cars(car1['specs'], car2['specs'], model)
                    comparisons.append({
                        'car1': car1,
                        'car2': car2,
                        'comparison': comparison
                    })
            
            # Display comparisons
            st.success("Comparison complete!")
            
            for comp in comparisons:
                st.subheader(f"Comparison: {comp['car1']['brand']} {comp['car1']['model']} vs {comp['car2']['brand']} {comp['car2']['model']}")
                
                # Display specifications side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{comp['car1']['brand']} {comp['car1']['model']} ({comp['car1']['year']})**")
                    st.json(comp['car1']['specs'])
                
                with col2:
                    st.write(f"**{comp['car2']['brand']} {comp['car2']['model']} ({comp['car2']['year']})**")
                    st.json(comp['car2']['specs'])
                
                # Display detailed comparison
                st.markdown(comp['comparison'])
                st.markdown("---")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Add instructions
st.markdown("""
### Instructions:
1. Review the cars to be compared
2. Click 'Compare Cars' to see detailed comparisons between all cars
3. Each comparison will show:
   - Overall comparison
   - Performance comparison
   - Technical specifications
   - Pros and cons
   - Recommendations
""") 