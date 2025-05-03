import streamlit as st
from PIL import Image
import io
import cv2
import numpy as np
# import google.generativeai as genai

# --- إعدادات أولية (يجب استبدالها) ---
# قم بإعداد مفتاح API الخاص بك (يفضل استخدام st.secrets)
# genai.configure(api_key="YOUR_GOOGLE_API_KEY")

# --- دوال مساعدة (تحتاج إلى تطبيق فعلي) ---

def detect_and_blur_plate(image_bytes):
    """
    (Placeholder) تكتشف وتموه لوحة الترخيص في الصورة.
    تحتاج هذه الدالة إلى تطبيق فعلي باستخدام OpenCV ونموذج اكتشاف كائنات.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_cv = np.array(image)
        # --- منطق اكتشاف اللوحة (مثال بسيط باستخدام Haar Cascade - يحتاج تدريب أو ملف XML جاهز) ---
        # gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
        # plate_cascade = cv2.CascadeClassifier('path/to/haarcascade_russian_plate_number.xml') # تحتاج ملف XML
        # plates = plate_cascade.detectMultiScale(gray, 1.1, 4)
        # for (x, y, w, h) in plates:
        #     roi = img_cv[y:y+h, x:x+w]
        #     roi = cv2.GaussianBlur(roi, (23, 23), 30) # تطبيق التمويه
        #     img_cv[y:y+roi.shape[0], x:x+roi.shape[1]] = roi # إعادة الجزء المموه للصورة الأصلية

        # --- حل مؤقت: تمويه جزء افتراضي من الصورة ---
        h, w = img_cv.shape[:2]
        # تمويه منطقة أسفل الوسط (كمثال)
        blur_zone = img_cv[int(h*0.7):int(h*0.9), int(w*0.3):int(w*0.7)]
        if blur_zone.size > 0:
             blurred_roi = cv2.GaussianBlur(blur_zone, (51, 51), 30)
             img_cv[int(h*0.7):int(h*0.9), int(w*0.3):int(w*0.7)] = blurred_roi
        # --- نهاية الحل المؤقت ---

        blurred_image_pil = Image.fromarray(img_cv)
        buf = io.BytesIO()
        blurred_image_pil.save(buf, format='PNG')
        blurred_image_bytes = buf.getvalue()
        return blurred_image_bytes
    except Exception as e:
        st.error(f"خطأ في معالجة الصورة: {e}")
        return image_bytes # إرجاع الصورة الأصلية في حالة الفشل

def call_gemini_vision(image_bytes, text_prompt):
    """
    (Placeholder) تستدعي Gemini API لتحليل الصورة والنص.
    تحتاج إلى تطبيق فعلي لاستدعاء API.
    """
    # model = genai.GenerativeModel('gemini-pro-vision') # أو النموذج الأحدث المناسب
    # image_parts = [{"mime_type": "image/png", "data": image_bytes}]
    # response = model.generate_content([text_prompt, image_parts])
    # return response.text
    # --- رد وهمي للتجربة ---
    return f"""
    **السيارة المحددة:** تويوتا كامري 2022 (تقديري)
    **المواصفات:** محرك 4 سلندر 2.5 لتر، ناقل حركة أوتوماتيكي 8 سرعات، دفع أمامي.
    **المميزات:** موثوقية عالية، استهلاك وقود جيد، مقصورة واسعة.
    **العيوب الشائعة:** تصميم داخلي قديم بعض الشيء، تسارع متوسط.
    """

def call_gemini_text(text_prompt):
    """
    (Placeholder) تستدعي Gemini API لمعالجة النصوص (للبحث عن الأسعار، الوقود، المقارنة).
    تحتاج إلى تطبيق فعلي لاستدعاء API.
    """
    # model = genai.GenerativeModel('gemini-pro') # أو النموذج الأحدث
    # response = model.generate_content(text_prompt)
    # return response.text
    # --- ردود وهمية للتجربة ---
    if "سعر السوق" in text_prompt:
        return "متوسط سعر السوق المقدر في البلد المحدد: 25,000 - 28,000 دولار أمريكي (كمثال)."
    elif "أسعار الوقود" in text_prompt:
        return "أسعار الوقود الحالية في البلد المحدد: بنزين 95: 1.8 دولار/لتر، ديزل: 1.6 دولار/لتر (كمثال)."
    elif "قارن بين" in text_prompt:
        return "بناءً على المقارنة، السيارة 1 (تويوتا كامري) تبدو خيارًا أفضل للموثوقية وتكاليف التشغيل طويلة الأمد، بينما السيارة 2 (هوندا أكورد) قد توفر تجربة قيادة رياضية أكثر."
    elif "نصيحتك بشرائها" in text_prompt:
        return "**التقييم: 8/10** \nسيارة موثوقة واقتصادية ومناسبة للاستخدام اليومي. سعرها في السوق معقول. العيوب المذكورة ليست جوهرية لمعظم المستخدمين."
    else:
        return "استجابة نصية من Gemini (Placeholder)."


# --- واجهة المستخدم Streamlit ---
st.set_page_config(layout="wide", page_title="مساعد شراء السيارات الذكي")
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

    uploaded_file = st.camera_input("📸 التقط صورة لسيارة جديدة للمقارنة", key=f"compare_cam_{len(st.session_state.cars_to_compare)}")
    # أو استخدم رفع الملفات:
    # uploaded_file = st.file_uploader("أو ارفع صورة سيارة", type=['jpg', 'png', 'jpeg'], key=f"compare_upload_{len(st.session_state.cars_to_compare)}")


    if uploaded_file is not None:
        img_bytes = uploaded_file.getvalue()
        st.image(img_bytes, caption="الصورة الأصلية", width=300)

        with st.spinner("⏳ جارٍ معالجة الصورة وتحليل السيارة..."):
            # 1. تمويه اللوحة
            blurred_bytes = detect_and_blur_plate(img_bytes)
            st.image(blurred_bytes, caption="الصورة المعالجة (اللوحة مموهة)", width=300)

            # 2. استدعاء Gemini Vision للتحليل
            vision_prompt = "حلل هذه الصورة لسيارة. حدد الماركة، الموديل، والسنة التقديرية. اذكر المواصفات الرئيسية والعيوب الشائعة المعروفة. تجاهل لوحة الترخيص."
            car_info = call_gemini_vision(blurred_bytes, vision_prompt)

            # (تحسين مستقبلي: استخلاص بيانات منظمة من car_info)
            car_data = {
                "id": f"car_{len(st.session_state.cars_to_compare)}",
                "image": blurred_bytes,
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
                st.image(car["image"], caption=f"سيارة {i+1}", use_column_width=True)
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
                         st.image(car["image"], caption=f"سيارة {i+1}", use_column_width=True)
                         st.markdown(f"**المعلومات:**\n {car['info']}")
                         st.success(f"**السعر المقدر:**\n {car.get('market_price', 'غير متوفر')}")


                st.markdown("**💡 التوصية النهائية للذكاء الاصطناعي:**")
                st.success(final_recommendation)


# --- منطق وضع التقييم الفردي ---
elif app_mode == "✔️ تقييم سيارة واحدة":
    st.header("✔️ تقييم سيارة واحدة")
    st.write("التقط صورة للسيارة التي تريد تقييمها:")

    uploaded_file_single = st.camera_input("📸 التقط صورة السيارة", key="single_cam")
    # أو استخدم رفع الملفات:
    # uploaded_file_single = st.file_uploader("أو ارفع صورة السيارة", type=['jpg', 'png', 'jpeg'], key="single_upload")


    if uploaded_file_single is not None:
        img_bytes_single = uploaded_file_single.getvalue()
        st.image(img_bytes_single, caption="الصورة الأصلية", width=400)

        if st.button("🧐 قيّم هذه السيارة", key="evaluate_button"):
            with st.spinner("⏳ جارٍ تحليل السيارة والبحث عن المعلومات..."):
                # 1. تمويه اللوحة
                blurred_bytes_single = detect_and_blur_plate(img_bytes_single)
                st.image(blurred_bytes_single, caption="الصورة المعالجة (اللوحة مموهة)", width=400)

                # 2. استدعاء Gemini Vision للتحليل
                vision_prompt_single = "حلل هذه الصورة لسيارة. حدد الماركة، الموديل، والسنة التقديرية. اذكر المواصفات الرئيسية والعيوب الشائعة المعروفة. تجاهل لوحة الترخيص."
                car_info_single = call_gemini_vision(blurred_bytes_single, vision_prompt_single)

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