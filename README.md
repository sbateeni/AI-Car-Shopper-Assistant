# Car Type Detector

A Streamlit application that uses Google's Gemini AI model to detect car types from images.

## Features

- Upload car images
- Use camera to take photos
- AI-powered car type detection using Gemini Vision
- Detailed car information including make, model, year, and type

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Open the application in your web browser
2. Choose between uploading an image or using your camera
3. Click the "Detect Car Type" button
4. View the results showing the detected car make, model, year, and type

## Requirements

- Python 3.7+
- Streamlit
- Pillow
- Google Generative AI
- Python-dotenv
- Gemini API key 