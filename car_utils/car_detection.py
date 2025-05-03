from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
from PIL import Image
import io
import streamlit as st

def load_model():
    """تحميل نموذج Swin Transformer من Hugging Face"""
    try:
        processor = AutoImageProcessor.from_pretrained("microsoft/swin-base-patch4-window7-224-in22k")
        model = AutoModelForImageClassification.from_pretrained("microsoft/swin-base-patch4-window7-224-in22k")
        return processor, model
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {e}")
        return None, None

def analyze_car(image_bytes):
    """
    تحليل الصورة باستخدام Swin Transformer
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
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        confidence = torch.nn.functional.softmax(logits, dim=-1)[0][predicted_class_idx].item()
        
        # تحضير وصف للنتيجة
        car_description = f"تم تحليل الصورة بثقة {confidence:.2f}"
        
        return image, car_description
        
    except Exception as e:
        st.error(f"خطأ في تحليل الصورة: {e}")
        return None, "حدث خطأ أثناء تحليل الصورة" 