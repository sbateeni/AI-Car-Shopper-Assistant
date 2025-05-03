import io
import base64
from PIL import Image, ImageFilter
import streamlit as st
from .config import BLUR_SETTINGS

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
    تمويه منطقة لوحة الترخيص في الصورة
    """
    try:
        # تحويل الصورة إلى تنسيق PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # تمويه منطقة افتراضية
        width, height = image.size
        region = BLUR_SETTINGS["region"]
        
        # تحديد منطقة التمويه
        x1 = int(width * region["width_start"])
        y1 = int(height * region["height_start"])
        x2 = int(width * region["width_end"])
        y2 = int(height * region["height_end"])
        
        # قص المنطقة المراد تمويهها
        region_to_blur = image.crop((x1, y1, x2, y2))
        
        # تطبيق التمويه
        blur_params = BLUR_SETTINGS["blur"]
        blurred_region = region_to_blur.filter(ImageFilter.GaussianBlur(radius=blur_params["sigma"]))
        
        # لصق المنطقة المموهة في الصورة الأصلية
        image.paste(blurred_region, (x1, y1))
        
        return image
        
    except Exception as e:
        st.error(f"خطأ في معالجة الصورة: {e}")
        return None 