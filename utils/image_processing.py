import io
import base64
from PIL import Image
import cv2
import numpy as np
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
    تكتشف وتموه لوحة الترخيص في الصورة.
    """
    try:
        # تحويل الصورة إلى تنسيق OpenCV
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img_cv = np.array(image)
        
        # تمويه منطقة افتراضية
        h, w = img_cv.shape[:2]
        region = BLUR_SETTINGS["region"]
        blur_zone = img_cv[
            int(h * region["height_start"]):int(h * region["height_end"]),
            int(w * region["width_start"]):int(w * region["width_end"])
        ]
        
        if blur_zone.size > 0:
            blur_params = BLUR_SETTINGS["blur"]
            blurred_roi = cv2.GaussianBlur(
                blur_zone,
                blur_params["kernel_size"],
                blur_params["sigma"]
            )
            img_cv[
                int(h * region["height_start"]):int(h * region["height_end"]),
                int(w * region["width_start"]):int(w * region["width_end"])
            ] = blurred_roi

        # تحويل الصورة المعالجة إلى تنسيق base64
        blurred_image_pil = Image.fromarray(img_cv)
        return image_to_base64(blurred_image_pil)
    except Exception as e:
        st.error(f"خطأ في معالجة الصورة: {e}")
        return base64.b64encode(image_bytes).decode() 