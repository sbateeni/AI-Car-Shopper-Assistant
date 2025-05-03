from transformers import AutoImageProcessor, AutoModelForObjectDetection
import torch
from PIL import Image, ImageDraw
import io
import streamlit as st

def load_model():
    """تحميل نموذج DETR من Hugging Face"""
    try:
        processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
        model = AutoModelForObjectDetection.from_pretrained("facebook/detr-resnet-50")
        return processor, model
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {e}")
        return None, None

def analyze_car(image_bytes):
    """
    تحليل الصورة باستخدام DETR
    """
    try:
        # تحميل النموذج
        processor, model = load_model()
        if processor is None or model is None:
            return None, "لم يتمكن من تحميل النموذج"

        # تحويل الصورة إلى تنسيق PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # تحويل الصورة إلى RGB إذا كانت في تنسيق آخر
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # معالجة الصورة
        inputs = processor(images=image, return_tensors="pt")
        
        # تحويل النموذج إلى وضع التقييم
        model.eval()
        
        # تحليل الصورة
        with torch.no_grad():
            outputs = model(**inputs)
        
        # تحليل النتائج
        probas = outputs.logits.softmax(-1)[0, :, :]
        
        # رسم المربعات حول الأشياء المكتشفة
        draw = ImageDraw.Draw(image)
        for score, box in zip(probas.max(-1).values, outputs.pred_boxes[0]):
            if score > 0.5:  # عتبة الثقة
                box = box.tolist()
                draw.rectangle(box, outline="red", width=2)
        
        # تحضير وصف للنتيجة
        car_description = "تم تحليل الصورة واكتشاف الأشياء فيها"
        
        return image, car_description
        
    except Exception as e:
        st.error(f"خطأ في تحليل الصورة: {e}")
        return None, "حدث خطأ أثناء تحليل الصورة" 