import sqlite3
import json
import base64
from io import BytesIO
from PIL import Image
import io

def init_db():
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  details TEXT,
                  specs TEXT,
                  image BLOB)''')
    conn.commit()
    conn.close()

def save_car(car_data):
    """Save car data to the database"""
    try:
        # Convert image to bytes if it exists
        image_bytes = None
        if car_data.get('image'):
            if car_data['image'].mode == 'RGBA':
                car_data['image'] = car_data['image'].convert('RGB')
            img_byte_arr = BytesIO()
            car_data['image'].save(img_byte_arr, format='JPEG')
            image_bytes = img_byte_arr.getvalue()
        
        # Save to database
        conn = sqlite3.connect('cars.db')
        c = conn.cursor()
        
        # Convert details and specs to JSON strings
        details_json = json.dumps(car_data['details'])
        specs_json = json.dumps(car_data['specs'])
        
        c.execute('''INSERT INTO cars (details, specs, image)
                    VALUES (?, ?, ?)''', (details_json, specs_json, image_bytes))
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error saving car: {str(e)}")
        return False

def get_all_cars():
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    c.execute('SELECT * FROM cars')
    cars = []
    for row in c.fetchall():
        car = {
            'id': row[0],
            'details': json.loads(row[1]),
            'specs': json.loads(row[2]),
            'image': Image.open(BytesIO(row[3])) if row[3] else None
        }
        cars.append(car)
    conn.close()
    return cars

def delete_car(car_id):
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    c.execute('DELETE FROM cars WHERE id = ?', (car_id,))
    conn.commit()
    conn.close()

# Initialize database when module is imported
init_db() 