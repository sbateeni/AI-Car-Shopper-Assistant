from PIL import Image, ImageDraw
import io
import streamlit as st

def detect_car(image_bytes):
    """
    تحليل الصورة باستخدام معالجة الصور الأساسية
    """
    try:
        # تحويل الصورة إلى تنسيق PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # تحليل الصورة
        width, height = image.size
        aspect_ratio = width / height
        
        # تحديد ما إذا كانت الصورة تحتوي على سيارة بناءً على نسبة العرض إلى الارتفاع
        is_car = 1.5 <= aspect_ratio <= 3.0
        
        if is_car:
            # رسم مربع حول المنطقة المتوقعة للسيارة
            draw = ImageDraw.Draw(image)
            margin = 0.1
            x1 = width * margin
            y1 = height * margin
            x2 = width * (1 - margin)
            y2 = height * (1 - margin)
            draw.rectangle([(x1, y1), (x2, y2)], outline="green", width=2)
            
            car_description = "تم الكشف عن سيارة في الصورة"
        else:
            car_description = "لم يتم العثور على سيارة في الصورة"
        
        return image, car_description
        
    except Exception as e:
        st.error(f"خطأ في تحليل الصورة: {e}")
        return None, "حدث خطأ أثناء تحليل الصورة" 