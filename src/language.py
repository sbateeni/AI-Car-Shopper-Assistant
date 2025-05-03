import streamlit as st

def get_language_prompts(language):
    """Get language-specific prompts"""
    if language == "Arabic":
        return {
            "detection_prompt": """قم بتحليل الصورة وتحديد معلومات السيارة. يجب أن تكون الإجابة بتنسيق JSON فقط، بدون أي نص إضافي قبل أو بعد JSON.

التنسيق المطلوب:
{
    "brand": "اسم الماركة",
    "model": "اسم الموديل",
    "year": "سنة الصنع",
    "type": "نوع السيارة"
}

لا تضع أي نص قبل أو بعد JSON.""",
            "specs_prompt": """قم بتوفير مواصفات السيارة {year} {brand} {model}. يجب أن تكون الإجابة بتنسيق JSON فقط، بدون أي نص إضافي قبل أو بعد JSON.

التنسيق المطلوب:
{
    "basic_info": {
        "brand": "اسم الماركة",
        "model": "اسم الموديل",
        "year": "سنة الصنع",
        "type": "نوع السيارة"
    },
    "performance": {
        "fuel_consumption": "استهلاك الوقود",
        "engine_size": "حجم المحرك",
        "cylinders": "عدد الأسطوانات",
        "transmission": "نوع ناقل الحركة",
        "fuel_type": "نوع الوقود",
        "horsepower": "قوة المحرك",
        "torque": "عزم الدوران",
        "top_speed": "السرعة القصوى",
        "acceleration": "التسارع"
    },
    "technical_specs": {
        "length": "الطول",
        "width": "العرض",
        "height": "الارتفاع",
        "wheelbase": "قاعدة العجلات",
        "weight": "الوزن",
        "seating_capacity": "سعة المقاعد",
        "trunk_capacity": "سعة الصندوق"
    },
    "features": {
        "price_range": "نطاق السعر",
        "safety_features": ["ميزات الأمان"],
        "comfort_features": ["ميزات الراحة"],
        "technology_features": ["ميزات التكنولوجيا"]
    }
}

لا تضع أي نص قبل أو بعد JSON."""
        }
    else:
        return {
            "detection_prompt": """Analyze the image and identify the car information. The response must be in JSON format only, with no additional text before or after the JSON.

Required format:
{
    "brand": "brand name",
    "model": "model name",
    "year": "manufacturing year",
    "type": "car type"
}

Do not include any text before or after the JSON.""",
            "specs_prompt": """Provide specifications for the {year} {brand} {model}. The response must be in JSON format only, with no additional text before or after the JSON.

Required format:
{
    "basic_info": {
        "brand": "brand name",
        "model": "model name",
        "year": "manufacturing year",
        "type": "car type"
    },
    "performance": {
        "fuel_consumption": "fuel consumption",
        "engine_size": "engine size",
        "cylinders": "number of cylinders",
        "transmission": "transmission type",
        "fuel_type": "fuel type",
        "horsepower": "horsepower",
        "torque": "torque",
        "top_speed": "top speed",
        "acceleration": "acceleration"
    },
    "technical_specs": {
        "length": "length",
        "width": "width",
        "height": "height",
        "wheelbase": "wheelbase",
        "weight": "weight",
        "seating_capacity": "seating capacity",
        "trunk_capacity": "trunk capacity"
    },
    "features": {
        "price_range": "price range",
        "safety_features": ["safety features"],
        "comfort_features": ["comfort features"],
        "technology_features": ["technology features"]
    }
}

Do not include any text before or after the JSON."""
        }

def get_language_texts(language):
    """Get language-specific UI texts"""
    if language == "Arabic":
        return {
            "title": "كاشف نوع السيارة",
            "description": "قم بتحميل صورة أو استخدم الكاميرا للكشف عن نوع السيارة والحصول على مواصفات تفصيلية",
            "upload": "تحميل صورة",
            "camera": "استخدام الكاميرا",
            "detect": "كشف نوع السيارة",
            "processing": "جاري المعالجة...",
            "success": "تم الكشف عن السيارة بنجاح!",
            "error": "حدث خطأ أثناء معالجة الصورة",
            "compare": "مقارنة مع سيارة أخرى",
            "uploaded_image": "الصورة المرفوعة",
            "specs": "المواصفات",
            "basic_info": "المعلومات الأساسية",
            "performance": "الأداء",
            "technical": "المواصفات الفنية",
            "features": "المميزات",
            "price": "نطاق السعر",
            "safety": "ميزات الأمان",
            "comfort": "ميزات الراحة",
            "tech": "ميزات التكنولوجيا"
        }
    else:
        return {
            "title": "Car Type Detector",
            "description": "Upload an image or use your camera to detect car type and get detailed specifications",
            "upload": "Upload an image",
            "camera": "Use camera",
            "detect": "Detect Car Type",
            "processing": "Processing...",
            "success": "Car detected successfully!",
            "error": "Error processing image",
            "compare": "Compare with Another Car",
            "uploaded_image": "Uploaded Image",
            "specs": "Specifications",
            "basic_info": "Basic Information",
            "performance": "Performance",
            "technical": "Technical Specifications",
            "features": "Features",
            "price": "Price Range",
            "safety": "Safety Features",
            "comfort": "Comfort Features",
            "tech": "Technology Features"
        } 