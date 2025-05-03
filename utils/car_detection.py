from transformers import ViTImageProcessor, ViTForImageClassification
import torch
from PIL import Image
import io
import streamlit as st

def load_model():
    """تحميل نموذج ViT من Hugging Face"""
    try:
        processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
        model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")
        return processor, model
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {e}")
        return None, None

def detect_car(image_bytes):
    """
    تحليل الصورة باستخدام ViT
    """
    try:
        # تحميل النموذج
        processor, model = load_model()
        if processor is None or model is None:
            return None, "لم يتمكن من تحميل النموذج"

        # تحويل الصورة إلى تنسيق PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # معالجة الصورة
        inputs = processor(images=image, return_tensors="pt")
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