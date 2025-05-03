import sqlite3
import json
import base64
from io import BytesIO
from PIL import Image

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
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    
    # Convert image to bytes
    img_byte_arr = BytesIO()
    
    # Convert RGBA to RGB if necessary
    if car_data['image'].mode == 'RGBA':
        car_data['image'] = car_data['image'].convert('RGB')
    
    car_data['image'].save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Convert details and specs to JSON strings
    details_json = json.dumps(car_data['details'])
    specs_json = json.dumps(car_data['specs'])
    
    c.execute('''INSERT INTO cars (details, specs, image)
                 VALUES (?, ?, ?)''', (details_json, specs_json, img_byte_arr))
    conn.commit()
    conn.close()

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
            'image': Image.open(BytesIO(row[3]))
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