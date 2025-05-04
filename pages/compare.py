import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re
from src.database import get_all_cars, delete_car

def clean_json_string(json_str):
    # Remove any text before or after the JSON object
    json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    
    # Remove any markdown formatting
    json_str = json_str.replace('```json', '').replace('```', '')
    
    # Remove any whitespace at the beginning and end
    json_str = json_str.strip()
    
    return json_str

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = st.session_state.get('api_key', os.getenv('GEMINI_API_KEY', ''))
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("يرجى إدخال مفتاح Gemini API في الصفحة الرئيسية أولاً.")
    st.stop()

# Initialize model
model = genai.GenerativeModel('models/gemini-2.0-flash-001')

# Get all cars from database
detected_cars = get_all_cars()

# Language selection
language = st.sidebar.selectbox(
    "Select Language / اختر اللغة",
    ["English", "Arabic"]
)

# Get language-specific texts
texts = {
    "English": {
        "title": "Car Comparison",
        "description": "Compare cars based on their specifications",
        "detected_cars": "Detected Cars",
        "delete": "Delete",
        "view": "View Details",
        "compare": "Compare Cars",
        "overall": "Overall Comparison",
        "performance": "Performance Comparison",
        "technical": "Technical Specifications",
        "features": "Features",
        "pros_cons": "Pros and Cons",
        "recommendation": "Recommendation",
        "no_cars": "No cars detected. Please go back to the main page and detect some cars first.",
        "select_cars": "Select cars to compare",
        "delete_confirm": "Are you sure you want to delete this car?",
        "select_first": "Select first car",
        "select_second": "Select second car",
        "basic_info": "Basic Information",
        "price": "Price Range",
        "safety": "Safety Features",
        "comfort": "Comfort Features",
        "tech": "Technology Features"
    },
    "Arabic": {
        "title": "مقارنة السيارات",
        "description": "قارن بين السيارات بناءً على مواصفاتها",
        "detected_cars": "السيارات المكتشفة",
        "delete": "حذف",
        "view": "عرض التفاصيل",
        "compare": "مقارنة السيارات",
        "overall": "مقارنة عامة",
        "performance": "مقارنة الأداء",
        "technical": "المواصفات الفنية",
        "features": "المميزات",
        "pros_cons": "الإيجابيات والسلبيات",
        "recommendation": "التوصية",
        "no_cars": "لم يتم اكتشاف أي سيارات. يرجى العودة إلى الصفحة الرئيسية واكتشاف بعض السيارات أولاً.",
        "select_cars": "اختر السيارات للمقارنة",
        "delete_confirm": "هل أنت متأكد من حذف هذه السيارة؟",
        "select_first": "اختر السيارة الأولى",
        "select_second": "اختر السيارة الثانية",
        "basic_info": "المعلومات الأساسية",
        "price": "نطاق السعر",
        "safety": "مميزات الأمان",
        "comfort": "مميزات الراحة",
        "tech": "المميزات التكنولوجية"
    }
}

# Main title and description
st.title(texts[language]["title"])
st.write(texts[language]["description"])

# Display detected cars
st.subheader(texts[language]["detected_cars"])

if not detected_cars:
    st.warning(texts[language]["no_cars"])
    st.stop()

# Initialize selected cars in session state if not exists
if 'selected_cars' not in st.session_state:
    st.session_state.selected_cars = []

# Display cars in a grid
cols = st.columns(3)
for i, car in enumerate(detected_cars):
    with cols[i % 3]:
        st.image(car['image'], width=200)
        st.write(f"**{car['details']['brand']} {car['details']['model']} ({car['details']['year']})**")
        st.write(f"**Type:** {car['details']['type']}")
        
        # Create two columns for buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # View button
            if st.button(f"{texts[language]['view']} {i+1}", key=f"view_{i}"):
                st.session_state['viewing_car'] = car
                st.rerun()
        
        with col2:
            # Compare checkbox
            if st.checkbox(f"{texts[language]['compare']} {i+1}", key=f"compare_{i}"):
                if car not in st.session_state.selected_cars:
                    st.session_state.selected_cars.append(car)
            else:
                if car in st.session_state.selected_cars:
                    st.session_state.selected_cars.remove(car)

# Check if we're viewing a car's details
if 'viewing_car' in st.session_state:
    car = st.session_state['viewing_car']
    
    # Display car details
    st.subheader(f"{car['details']['brand']} {car['details']['model']} ({car['details']['year']})")
    
    # Basic Information
    st.subheader(texts[language]["basic_info"])
    st.write(f"**Brand:** {car['details']['brand']}")
    st.write(f"**Model:** {car['details']['model']}")
    st.write(f"**Year:** {car['details']['year']}")
    st.write(f"**Type:** {car['details']['type']}")
    
    # Performance
    st.subheader(texts[language]["performance"])
    performance = car['specs']['performance']
    st.write(f"**Fuel Consumption:** {performance['fuel_consumption']}")
    st.write(f"**Engine Size:** {performance['engine_size']}")
    st.write(f"**Cylinders:** {performance['cylinders']}")
    st.write(f"**Transmission:** {performance['transmission']}")
    st.write(f"**Fuel Type:** {performance['fuel_type']}")
    st.write(f"**Horsepower:** {performance['horsepower']}")
    st.write(f"**Torque:** {performance['torque']}")
    st.write(f"**Top Speed:** {performance['top_speed']}")
    st.write(f"**Acceleration:** {performance['acceleration']}")
    
    # Technical Specifications
    st.subheader(texts[language]["technical"])
    tech_specs = car['specs']['technical_specs']
    st.write(f"**Length:** {tech_specs['length']}")
    st.write(f"**Width:** {tech_specs['width']}")
    st.write(f"**Height:** {tech_specs['height']}")
    st.write(f"**Wheelbase:** {tech_specs['wheelbase']}")
    st.write(f"**Weight:** {tech_specs['weight']}")
    st.write(f"**Seating Capacity:** {tech_specs['seating_capacity']}")
    st.write(f"**Trunk Capacity:** {tech_specs['trunk_capacity']}")
    
    # Features
    st.subheader(texts[language]["features"])
    features = car['specs']['features']
    st.write(f"**{texts[language]['price']}:** {features['price_range']}")
    
    st.write(f"**{texts[language]['safety']}:**")
    for feature in features["safety_features"]:
        st.write(f"- {feature}")
        
    st.write(f"**{texts[language]['comfort']}:**")
    for feature in features["comfort_features"]:
        st.write(f"- {feature}")
        
    st.write(f"**{texts[language]['tech']}:**")
    for feature in features["technology_features"]:
        st.write(f"- {feature}")
    
    # Back button
    if st.button("Back to Comparison"):
        del st.session_state['viewing_car']
        st.rerun()
    
    st.stop()

# Compare selected cars
if len(st.session_state.selected_cars) >= 2:
    if st.button(texts[language]["compare"]):
        try:
            car1 = st.session_state.selected_cars[0]
            car2 = st.session_state.selected_cars[1]
            
            # Get specifications for both cars
            prompt = f"""قم بمقارنة السيارتين التاليتين مع التركيز على المخرجات والمواصفات الفنية المهمة للمشتري:
            
            السيارة الأولى: {car1['details']['year']} {car1['details']['brand']} {car1['details']['model']}
            السيارة الثانية: {car2['details']['year']} {car2['details']['brand']} {car2['details']['model']}
            
            قدم المقارنة بالتنسيق التالي:
            {{
                "engine_comparison": {{
                    "car1": {{
                        "power": "قوة المحرك بالحصان",
                        "torque": "عزم الدوران",
                        "acceleration": "التسارع من 0-100 كم/س",
                        "top_speed": "السرعة القصوى"
                    }},
                    "car2": {{
                        "power": "قوة المحرك بالحصان",
                        "torque": "عزم الدوران",
                        "acceleration": "التسارع من 0-100 كم/س",
                        "top_speed": "السرعة القصوى"
                    }},
                    "winner": "السيارة الأفضل من حيث الأداء",
                    "reason": "سبب التفوق في الأداء"
                }},
                "fuel_efficiency": {{
                    "car1": {{
                        "city": "استهلاك الوقود في المدينة",
                        "highway": "استهلاك الوقود على الطرق السريعة",
                        "combined": "متوسط استهلاك الوقود"
                    }},
                    "car2": {{
                        "city": "استهلاك الوقود في المدينة",
                        "highway": "استهلاك الوقود على الطرق السريعة",
                        "combined": "متوسط استهلاك الوقود"
                    }},
                    "winner": "السيارة الأكثر كفاءة في استهلاك الوقود",
                    "reason": "سبب التفوق في كفاءة استهلاك الوقود"
                }},
                "maintenance": {{
                    "car1": {{
                        "service_interval": "فترة الصيانة",
                        "maintenance_cost": "تكلفة الصيانة",
                        "reliability": "الموثوقية"
                    }},
                    "car2": {{
                        "service_interval": "فترة الصيانة",
                        "maintenance_cost": "تكلفة الصيانة",
                        "reliability": "الموثوقية"
                    }},
                    "winner": "السيارة الأقل تكلفة في الصيانة",
                    "reason": "سبب التفوق في الصيانة"
                }},
                "value_for_money": {{
                    "car1": {{
                        "price": "السعر",
                        "resale_value": "قيمة إعادة البيع",
                        "features": "المميزات مقابل السعر"
                    }},
                    "car2": {{
                        "price": "السعر",
                        "resale_value": "قيمة إعادة البيع",
                        "features": "المميزات مقابل السعر"
                    }},
                    "winner": "السيارة الأفضل من حيث القيمة مقابل السعر",
                    "reason": "سبب التفوق في القيمة مقابل السعر"
                }},
                "final_recommendation": {{
                    "best_choice": "السيارة الموصى بها للشراء",
                    "reason": "سبب التوصية",
                    "suitable_for": "مناسبة لمن؟",
                    "considerations": "نقاط يجب مراعاتها قبل الشراء"
                }}
            }}
            
            يجب أن تكون جميع الإجابات باللغة العربية.
            قم بإرجاع كائن JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن."""
            
            response = model.generate_content(prompt)
            
            # Clean and parse the response
            response_text = clean_json_string(response.text)
            
            # Debug: Print the cleaned response
            st.write("الاستجابة بعد التنظيف:", response_text)
            
            # Try to parse the JSON
            try:
                comparison = json.loads(response_text)
                
                # Display comparison results
                st.subheader("مقارنة المحرك والأداء")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{car1['details']['brand']} {car1['details']['model']}:**")
                    st.write(f"قوة المحرك: {comparison['engine_comparison']['car1']['power']}")
                    st.write(f"عزم الدوران: {comparison['engine_comparison']['car1']['torque']}")
                    st.write(f"التسارع: {comparison['engine_comparison']['car1']['acceleration']}")
                    st.write(f"السرعة القصوى: {comparison['engine_comparison']['car1']['top_speed']}")
                
                with col2:
                    st.write(f"**{car2['details']['brand']} {car2['details']['model']}:**")
                    st.write(f"قوة المحرك: {comparison['engine_comparison']['car2']['power']}")
                    st.write(f"عزم الدوران: {comparison['engine_comparison']['car2']['torque']}")
                    st.write(f"التسارع: {comparison['engine_comparison']['car2']['acceleration']}")
                    st.write(f"السرعة القصوى: {comparison['engine_comparison']['car2']['top_speed']}")
                
                st.write(f"**النتيجة:** {comparison['engine_comparison']['winner']}")
                st.write(f"**السبب:** {comparison['engine_comparison']['reason']}")
                
                st.subheader("كفاءة استهلاك الوقود")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{car1['details']['brand']} {car1['details']['model']}:**")
                    st.write(f"في المدينة: {comparison['fuel_efficiency']['car1']['city']}")
                    st.write(f"على الطرق السريعة: {comparison['fuel_efficiency']['car1']['highway']}")
                    st.write(f"المتوسط: {comparison['fuel_efficiency']['car1']['combined']}")
                
                with col2:
                    st.write(f"**{car2['details']['brand']} {car2['details']['model']}:**")
                    st.write(f"في المدينة: {comparison['fuel_efficiency']['car2']['city']}")
                    st.write(f"على الطرق السريعة: {comparison['fuel_efficiency']['car2']['highway']}")
                    st.write(f"المتوسط: {comparison['fuel_efficiency']['car2']['combined']}")
                
                st.write(f"**النتيجة:** {comparison['fuel_efficiency']['winner']}")
                st.write(f"**السبب:** {comparison['fuel_efficiency']['reason']}")
                
                st.subheader("تكاليف الصيانة")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{car1['details']['brand']} {car1['details']['model']}:**")
                    st.write(f"فترة الصيانة: {comparison['maintenance']['car1']['service_interval']}")
                    st.write(f"تكلفة الصيانة: {comparison['maintenance']['car1']['maintenance_cost']}")
                    st.write(f"الموثوقية: {comparison['maintenance']['car1']['reliability']}")
                
                with col2:
                    st.write(f"**{car2['details']['brand']} {car2['details']['model']}:**")
                    st.write(f"فترة الصيانة: {comparison['maintenance']['car2']['service_interval']}")
                    st.write(f"تكلفة الصيانة: {comparison['maintenance']['car2']['maintenance_cost']}")
                    st.write(f"الموثوقية: {comparison['maintenance']['car2']['reliability']}")
                
                st.write(f"**النتيجة:** {comparison['maintenance']['winner']}")
                st.write(f"**السبب:** {comparison['maintenance']['reason']}")
                
                st.subheader("القيمة مقابل السعر")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**{car1['details']['brand']} {car1['details']['model']}:**")
                    st.write(f"السعر: {comparison['value_for_money']['car1']['price']}")
                    st.write(f"قيمة إعادة البيع: {comparison['value_for_money']['car1']['resale_value']}")
                    st.write(f"المميزات مقابل السعر: {comparison['value_for_money']['car1']['features']}")
                
                with col2:
                    st.write(f"**{car2['details']['brand']} {car2['details']['model']}:**")
                    st.write(f"السعر: {comparison['value_for_money']['car2']['price']}")
                    st.write(f"قيمة إعادة البيع: {comparison['value_for_money']['car2']['resale_value']}")
                    st.write(f"المميزات مقابل السعر: {comparison['value_for_money']['car2']['features']}")
                
                st.write(f"**النتيجة:** {comparison['value_for_money']['winner']}")
                st.write(f"**السبب:** {comparison['value_for_money']['reason']}")
                
                st.subheader("التوصية النهائية")
                st.write(f"**السيارة الموصى بها:** {comparison['final_recommendation']['best_choice']}")
                st.write(f"**سبب التوصية:** {comparison['final_recommendation']['reason']}")
                st.write(f"**مناسبة لمن؟** {comparison['final_recommendation']['suitable_for']}")
                st.write(f"**نقاط يجب مراعاتها قبل الشراء:** {comparison['final_recommendation']['considerations']}")
                
            except json.JSONDecodeError as e:
                st.error(f"خطأ في تحليل استجابة المقارنة: {str(e)}")
                st.error(f"الاستجابة الخام: {response.text}")
            
        except Exception as e:
            st.error(f"خطأ في مقارنة السيارات: {str(e)}")
else:
    st.warning("يجب اختيار سيارتين على الأقل للمقارنة")

def compare_cars(car1, car2, language):
    try:
        # Prepare the comparison prompt
        comparison_prompt = f"""قم بمقارنة السيارتين التاليتين:
        السيارة الأولى: {car1['details']['year']} {car1['details']['brand']} {car1['details']['model']}
        السيارة الثانية: {car2['details']['year']} {car2['details']['brand']} {car2['details']['model']}
        
        قم بإرجاع النتيجة بتنسيق JSON فقط، بدون أي نص إضافي قبل أو بعد الكائن.
        يجب أن تكون جميع الإجابات باللغة العربية.
        
        {{
            "general_comparison": {{
                "winner": "السيارة الفائزة في المقارنة العامة",
                "reason": "سبب الفوز"
            }},
            "performance": {{
                "car1": "أداء السيارة الأولى",
                "car2": "أداء السيارة الثانية",
                "winner": "السيارة الأفضل في الأداء",
                "reason": "سبب التفوق في الأداء"
            }},
            "technical_specs": {{
                "car1": "المواصفات الفنية للسيارة الأولى",
                "car2": "المواصفات الفنية للسيارة الثانية",
                "winner": "السيارة الأفضل في المواصفات الفنية",
                "reason": "سبب التفوق في المواصفات الفنية"
            }},
            "features": {{
                "car1": "مميزات السيارة الأولى",
                "car2": "مميزات السيارة الثانية",
                "winner": "السيارة الأفضل في المميزات",
                "reason": "سبب التفوق في المميزات"
            }},
            "recommendation": {{
                "best_choice": "السيارة الموصى بها",
                "reason": "سبب التوصية",
                "suitable_for": "مناسبة لمن؟"
            }}
        }}"""
        
        # Generate comparison
        response = model.generate_content(comparison_prompt)
        
        # Clean and parse the response
        response_text = clean_json_string(response.text)
        
        # Debug: Print the cleaned response
        st.write("الاستجابة بعد التنظيف:", response_text)
        
        # Try to parse the JSON
        try:
            comparison = json.loads(response_text)
            return comparison
        except json.JSONDecodeError as e:
            st.error(f"خطأ في تحليل استجابة المقارنة: {str(e)}")
            st.error(f"الاستجابة الخام: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"خطأ في مقارنة السيارات: {str(e)}")
        return None 