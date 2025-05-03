from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image, ImageDraw
import io
import streamlit as st
import os

def load_model():
    """تحميل نموذج DETR من Hugging Face"""
    try:
        processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
        return processor, model
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {e}")
        return None, None

def detect_car(image_bytes):
    """
    كشف وتحليل السيارة في الصورة باستخدام DETR
    """
    try:
        # تحميل النموذج
        processor, model = load_model()
        if processor is None or model is None:
            return None, "لم يتمكن من تحميل نموذج الكشف"

        # تحويل الصورة إلى تنسيق PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # معالجة الصورة
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        
        # تحويل النتائج إلى تنسيق قابل للقراءة
        target_sizes = torch.tensor([image.size[::-1]])
        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)[0]
        
        # البحث عن السيارات في النتائج
        cars = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            if model.config.id2label[label.item()] == "car":
                cars.append({
                    'bbox': box.tolist(),
                    'confidence': score.item()
                })
        
        if not cars:
            return None, "لم يتم العثور على سيارة في الصورة"
        
        # اختيار السيارة الأكثر وضوحاً (أعلى ثقة)
        best_car = max(cars, key=lambda x: x['confidence'])
        
        # رسم المربع المحيط بالسيارة
        x1, y1, x2, y2 = best_car['bbox']
        draw = ImageDraw.Draw(image)
        draw.rectangle([(x1, y1), (x2, y2)], outline="green", width=2)
        
        # تحضير وصف للسيارة
        car_description = f"تم الكشف عن سيارة بثقة {best_car['confidence']:.2f}"
        
        return image, car_description
        
    except Exception as e:
        st.error(f"خطأ في تحليل الصورة: {e}")
        return None, "حدث خطأ أثناء تحليل الصورة" 