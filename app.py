import streamlit as st
from PIL import Image
import io
import cv2
import numpy as np
import google.generativeai as genai
import base64

# --- إعدادات أولية ---
# تكوين مفتاح API باستخدام Streamlit secrets
if 'GOOGLE_API_KEY' in st.secrets:
    genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])
else:
    st.error("⚠️ لم يتم العثور على مفتاح API. يرجى إضافة مفتاح API في إعدادات Streamlit secrets.")
    st.stop()

# --- دوال مساعدة (تحتاج إلى تطبيق فعلي) ---

def image_to_base64(image):
    """تحويل الصورة إلى تنسيق base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(base64_string):
    """تحويل base64 إلى صورة"""
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def detect_and_blur_plate(image_bytes):
    """
    (Placeholder) تكتشف وتموه لوحة الترخيص في الصورة.
    تحتاج هذه الدالة إلى تطبيق فعلي باستخدام OpenCV ونموذج اكتشاف كائنات.
    """
    try:
        # تحويل الصورة إلى تنسيق OpenCV
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_cv = np.array(image)
        
        # تمويه منطقة افتراضية
        h, w = img_cv.shape[:2]
        blur_zone = img_cv[int(h*0.7):int(h*0.9), int(w*0.3):int(w*0.7)]
        if blur_zone.size > 0:
            blurred_roi = cv2.GaussianBlur(blur_zone, (51, 51), 30)
            img_cv[int(h*0.7):int(h*0.9), int(w*0.3):int(w*0.7)] = blurred_roi

        # تحويل الصورة المعالجة إلى تنسيق base64
        blurred_image_pil = Image.fromarray(img_cv)
        return image_to_base64(blurred_image_pil)
    except Exception as e:
        st.error(f"خطأ في معالجة الصورة: {e}")
        return base64.b64encode(image_bytes).decode()

def call_gemini_vision(image_base64, text_prompt):
    """
    (Placeholder) تستدعي Gemini API لتحليل الصورة والنص.
    تحتاج إلى تطبيق فعلي لاستدعاء API.
    """
    try:
        model = genai.GenerativeModel('gemini-pro-vision') # أو النموذج الأحدث المناسب
        image_parts = [{"mime_type": "image/png", "data": image_base64}]
        response = model.generate_content([text_prompt, image_parts])
        return response.text
    except Exception as e:
        st.error(f"خطأ في استدعاء Gemini API: {e}")
        return "عذراً، حدث خطأ في تحليل الصورة. يرجى المحاولة مرة أخرى."

def call_gemini_text(text_prompt):
    """
    (Placeholder) تستدعي Gemini API لمعالجة النصوص (للبحث عن الأسعار، الوقود، المقارنة).
    تحتاج إلى تطبيق فعلي لاستدعاء API.
    """
    try:
        model = genai.GenerativeModel('gemini-pro') # أو النموذج الأحدث
        response = model.generate_content(text_prompt)
        return response.text
    except Exception as e:
        st.error(f"خطأ في استدعاء Gemini API: {e}")
        return "عذراً، حدث خطأ في معالجة النص. يرجى المحاولة مرة أخرى."


# --- واجهة المستخدم Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="مساعد شراء السيارات الذكي",
    page_icon="🚗"
)
st.title("🚗 مساعد شراء السيارات الذكي")
st.markdown("قم بتصوير السيارات التي تفكر في شرائها للمقارنة أو التقييم.")

# --- إعدادات عامة (في الشريط الجانبي) ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    # مثال بسيط لقائمة الدول (يمكن توسيعها)
    countries = ["المملكة العربية السعودية", "الإمارات العربية المتحدة", "مصر", "الأردن", "الكويت", "أخرى"]
    selected_country = st.selectbox("اختر دولتك:", countries)

    st.header("🚦 وضع التشغيل")
    app_mode = st.radio("", ["📊 مقارنة عدة سيارات", "✔️ تقييم سيارة واحدة"])

    st.info("🔒 سيتم تمويه لوحات الترخيص تلقائيًا لحماية الخصوصية.")

# --- إدارة الحالة لتخزين السيارات المقارنة ---
if 'cars_to_compare' not in st.session_state:
    st.session_state.cars_to_compare = []

# --- منطق وضع المقارنة ---
if app_mode == "📊 مقارنة عدة سيارات":
    st.header("📊 مقارنة عدة سيارات")
    st.write("أضف صور السيارات التي تريد مقارنتها:")

    # إضافة خيارات إدخال الصور
    input_method = st.radio("اختر طريقة إدخال الصورة:", ["📸 التقاط صورة", "📁 رفع صورة"])
    
    if input_method == "📸 التقاط صورة":
        uploaded_file = st.camera_input("📸 التقط صورة لسيارة جديدة للمقارنة", key=f"compare_cam_{len(st.session_state.cars_to_compare)}")
    else:
        uploaded_file = st.file_uploader("📁 اختر صورة سيارة", type=['jpg', 'png', 'jpeg'], key=f"compare_upload_{len(st.session_state.cars_to_compare)}")

    if uploaded_file is not None:
        img_bytes = uploaded_file.getvalue()
        st.image(img_bytes, caption="الصورة الأصلية", width=300)

        with st.spinner("⏳ جارٍ معالجة الصورة وتحليل السيارة..."):
            # 1. تمويه اللوحة
            blurred_base64 = detect_and_blur_plate(img_bytes)
            blurred_image = base64_to_image(blurred_base64)
            st.image(blurred_image, caption="الصورة المعالجة (اللوحة مموهة)", width=300)

            # 2. استدعاء Gemini Vision للتحليل
            vision_prompt = "حلل هذه الصورة لسيارة. حدد الماركة، الموديل، والسنة التقديرية. اذكر المواصفات الرئيسية والعيوب الشائعة المعروفة. تجاهل لوحة الترخيص."
            car_info = call_gemini_vision(blurred_base64, vision_prompt)

            # (تحسين مستقبلي: استخلاص بيانات منظمة من car_info)
            car_data = {
                "id": f"car_{len(st.session_state.cars_to_compare)}",
                "image": blurred_base64,
                "info": car_info,
                "country": selected_country # حفظ الدولة مع السيارة
            }
            st.session_state.cars_to_compare.append(car_data)
            st.success("✅ تمت إضافة السيارة للمقارنة!")
            # إعادة تحميل الواجهة لتحديث العرض ومسح عنصر الإدخال
            st.rerun()

    # عرض السيارات المضافة للمقارنة
    if st.session_state.cars_to_compare:
        st.subheader("السيارات المضافة للمقارنة:")
        cols = st.columns(len(st.session_state.cars_to_compare))
        for i, car in enumerate(st.session_state.cars_to_compare):
            with cols[i]:
                car_image = base64_to_image(car["image"])
                st.image(car_image, caption=f"سيارة {i+1}", use_column_width=True)
                st.markdown(car["info"])
                if st.button(f"🗑️ إزالة السيارة {i+1}", key=f"remove_{car['id']}"):
                    st.session_state.cars_to_compare.pop(i)
                    st.rerun() # تحديث الواجهة بعد الإزالة

    # زر المقارنة النهائي
    if len(st.session_state.cars_to_compare) >= 2:
        if st.button("⚖️ قارن واختر الأفضل", key="compare_button"):
            with st.spinner(f"⏳ جارٍ البحث عن الأسعار في {selected_country} وإجراء المقارنة..."):
                # 1. جلب أسعار الوقود
                fuel_prompt = f"ما هي متوسط أسعار الوقود (بنزين وديزل) الحالية في {selected_country}؟"
                fuel_prices = call_gemini_text(fuel_prompt)
                st.session_state.fuel_prices = fuel_prices # تخزينها للعرض

                # 2. جلب أسعار السوق لكل سيارة وإعداد نص المقارنة
                comparison_input_parts = []
                for i, car in enumerate(st.session_state.cars_to_compare):
                    # (تحسين: استخلاص اسم السيارة وسنتها من car['info'])
                    car_name_year = f"السيارة {i+1} (المستخرجة من التحليل)"
                    price_prompt = f"ما هو متوسط سعر السوق لسيارة مثل '{car_name_year}' في {car['country']}؟"
                    market_price = call_gemini_text(price_prompt)
                    car['market_price'] = market_price # إضافة السعر لبيانات السيارة
                    comparison_input_parts.append(f"**السيارة {i+1}:**\n{car['info']}\n*السعر المقدر:* {market_price}\n---")

                # 3. استدعاء Gemini للمقارنة النهائية
                comparison_prompt = f"""
                قارن بين السيارات التالية بناءً على المعلومات المتوفرة:
                {''.join(comparison_input_parts)}

                مع الأخذ في الاعتبار أسعار الوقود في {selected_country}:
                {st.session_state.fuel_prices}

                أي سيارة تنصح بشرائها ولماذا؟ ركز على الموثوقية، التكلفة الإجمالية (شراء + تشغيل)، والملاءمة للاستخدام.
                """
                final_recommendation = call_gemini_text(comparison_prompt)

                # 4. عرض النتائج
                st.subheader("🏁 نتيجة المقارنة")
                st.info(f"**أسعار الوقود في {selected_country}:**\n{st.session_state.fuel_prices}")

                st.markdown("**ملخص السيارات وأسعارها:**")
                res_cols = st.columns(len(st.session_state.cars_to_compare))
                for i, car in enumerate(st.session_state.cars_to_compare):
                     with res_cols[i]:
                         car_image = base64_to_image(car["image"])
                         st.image(car_image, caption=f"سيارة {i+1}", use_column_width=True)
                         st.markdown(f"**المعلومات:**\n {car['info']}")
                         st.success(f"**السعر المقدر:**\n {car.get('market_price', 'غير متوفر')}")


                st.markdown("**💡 التوصية النهائية للذكاء الاصطناعي:**")
                st.success(final_recommendation)


# --- منطق وضع التقييم الفردي ---
elif app_mode == "✔️ تقييم سيارة واحدة":
    st.header("✔️ تقييم سيارة واحدة")
    st.write("أضف صورة السيارة التي تريد تقييمها:")

    # إضافة خيارات إدخال الصور
    input_method_single = st.radio("اختر طريقة إدخال الصورة:", ["📸 التقاط صورة", "📁 رفع صورة"], key="single_input_method")
    
    if input_method_single == "📸 التقاط صورة":
        uploaded_file_single = st.camera_input("📸 التقط صورة السيارة", key="single_cam")
    else:
        uploaded_file_single = st.file_uploader("📁 اختر صورة السيارة", type=['jpg', 'png', 'jpeg'], key="single_upload")

    if uploaded_file_single is not None:
        img_bytes_single = uploaded_file_single.getvalue()
        st.image(img_bytes_single, caption="الصورة الأصلية", width=400)

        if st.button("🧐 قيّم هذه السيارة", key="evaluate_button"):
            with st.spinner("⏳ جارٍ تحليل السيارة والبحث عن المعلومات..."):
                # 1. تمويه اللوحة
                blurred_base64_single = detect_and_blur_plate(img_bytes_single)
                blurred_image_single = base64_to_image(blurred_base64_single)
                st.image(blurred_image_single, caption="الصورة المعالجة (اللوحة مموهة)", width=400)

                # 2. استدعاء Gemini Vision للتحليل
                vision_prompt_single = "حلل هذه الصورة لسيارة. حدد الماركة، الموديل، والسنة التقديرية. اذكر المواصفات الرئيسية والعيوب الشائعة المعروفة. تجاهل لوحة الترخيص."
                car_info_single = call_gemini_vision(blurred_base64_single, vision_prompt_single)

                # (تحسين: استخلاص اسم وسنة السيارة من car_info_single)
                car_name_year_single = "السيارة المفردة (المستخرجة من التحليل)"

                # 3. جلب سعر السوق
                price_prompt_single = f"ما هو متوسط سعر السوق لسيارة مثل '{car_name_year_single}' في {selected_country}؟"
                market_price_single = call_gemini_text(price_prompt_single)

                # 4. جلب أسعار الوقود
                fuel_prompt_single = f"ما هي متوسط أسعار الوقود (بنزين وديزل) الحالية في {selected_country}؟"
                fuel_prices_single = call_gemini_text(fuel_prompt_single)

                # 5. استدعاء Gemini لتقديم النصح والتقييم
                advice_prompt = f"""
                حلل السيارة التالية:
                {car_info_single}

                معلومات إضافية:
                - الدولة: {selected_country}
                - متوسط سعر السوق المقدر: {market_price_single}
                - أسعار الوقود الحالية: {fuel_prices_single}

                بناءً على كل هذه العوامل (المواصفات، العيوب، السعر، تكلفة الوقود)، ما مدى نصيحتك بشراء هذه السيارة؟ قدم تقييمًا من 10 (حيث 10 هي الأعلى) مع تبرير واضح.
                """
                final_advice = call_gemini_text(advice_prompt)

                # عرض النتائج
                st.subheader("📝 نتيجة التقييم")
                st.markdown("**معلومات السيارة المحللة:**")
                st.write(car_info_single)
                st.info(f"**متوسط سعر السوق في {selected_country}:** {market_price_single}")
                st.info(f"**أسعار الوقود في {selected_country}:** {fuel_prices_single}")
                st.success(f"**💡 نصيحة الشراء (التقييم من 10):**\n{final_advice}")

# --- رسالة تذييل ---
st.markdown("---")
st.caption("تم التطوير باستخدام Streamlit و Python. يعتمد التحليل على Google Gemini API (الاستدعاءات الفعلية غير مطبقة هنا). تمويه اللوحة هو مثال توضيحي.") 