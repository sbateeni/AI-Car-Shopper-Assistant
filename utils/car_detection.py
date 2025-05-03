from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
import streamlit as st

def load_model():
    """تحميل نموذج YOLOv8"""
    try:
        model = YOLO('yolov8n.pt')
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
        cv2.rectangle(img_cv, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # تحويل الصورة المعالجة إلى تنسيق PIL
        processed_image = Image.fromarray(img_cv)
        
        # تحضير وصف للسيارة
        car_description = f"تم الكشف عن سيارة بثقة {best_car['confidence']:.2f}"
        
        return processed_image, car_description
        
    except Exception as e:
        st.error(f"خطأ في تحليل الصورة: {e}")
        return None, "حدث خطأ أثناء تحليل الصورة" 