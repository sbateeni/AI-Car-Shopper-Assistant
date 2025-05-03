from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageDraw
import io
import streamlit as st
import os

def load_model():
    """تحميل نموذج YOLOv8"""
    try:
        # تحميل النموذج من المسار المحلي
        model_path = os.path.join(os.path.dirname(__file__), 'yolov8n.pt')
        if not os.path.exists(model_path):
            # إذا لم يكن النموذج موجوداً، قم بتحميله
            model = YOLO('yolov8n.pt')
            model.save(model_path)
        else:
            model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"خطأ في تحميل النموذج: {e}")
        return None

def detect_car(image_bytes):
    """
    كشف وتحليل السيارة في الصورة باستخدام YOLOv8
    """
    try:
        # تحميل النموذج
        model = load_model()
        if model is None:
            return None, "لم يتمكن من تحميل نموذج الكشف"

        # تحويل الصورة إلى تنسيق OpenCV
        image = Image.open(io.BytesIO(image_bytes))
        img_cv = np.array(image)
        
        # الكشف عن الكائنات في الصورة
        results = model(img_cv)
        
        # البحث عن السيارات في النتائج
        cars = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                if int(box.cls) == 2:  # class 2 هو السيارة في YOLOv8
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = box.conf[0].item()
                    if confidence > 0.5:  # ثقة أعلى من 50%
                        cars.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': confidence
                        })
        
        if not cars:
            return None, "لم يتم العثور على سيارة في الصورة"
        
        # اختيار السيارة الأكثر وضوحاً (أعلى ثقة)
        best_car = max(cars, key=lambda x: x['confidence'])
        
        # رسم المربع المحيط بالسيارة
        x1, y1, x2, y2 = best_car['bbox']
        # استخدام PIL بدلاً من OpenCV للرسم
        draw = ImageDraw.Draw(image)
        draw.rectangle([(x1, y1), (x2, y2)], outline="green", width=2)
        
        # تحضير وصف للسيارة
        car_description = f"تم الكشف عن سيارة بثقة {best_car['confidence']:.2f}"
        
        return image, car_description
        
    except Exception as e:
        st.error(f"خطأ في تحليل الصورة: {e}")
        return None, "حدث خطأ أثناء تحليل الصورة" 