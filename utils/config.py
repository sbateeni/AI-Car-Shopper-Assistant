# إعدادات التطبيق
COUNTRIES = [
    "المملكة العربية السعودية",
    "الإمارات العربية المتحدة",
    "مصر",
    "الأردن",
    "الكويت",
    "أخرى"
]

# إعدادات معالجة الصور
BLUR_SETTINGS = {
    "region": {
        "height_start": 0.7,
        "height_end": 0.9,
        "width_start": 0.3,
        "width_end": 0.7
    },
    "blur": {
        "kernel_size": (51, 51),
        "sigma": 30
    }
}

# إعدادات واجهة المستخدم
UI_SETTINGS = {
    "page_config": {
        "layout": "wide",
        "page_title": "مساعد شراء السيارات الذكي",
        "page_icon": "🚗"
    },
    "image_display": {
        "original_width": 300,
        "processed_width": 300,
        "single_car_width": 400
    }
}

# إعدادات Gemini API
GEMINI_SETTINGS = {
    "vision_model": "gemini-pro-vision",
    "text_model": "gemini-pro"
} 