from flask import Flask, render_template, request
import qrcode
import os
import uuid
import sqlite3

app = Flask(__name__)

# ==========================================
# 1. تحديد المسار الكامل الإجباري للمشروع (عشان السيرفر مايتوهش)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# مسار مجلد الصور
QR_FOLDER = os.path.join(BASE_DIR, 'static', 'qrcodes')
os.makedirs(QR_FOLDER, exist_ok=True)

# مسار قاعدة البيانات
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# ==========================================
# دالة لإنشاء قاعدة البيانات
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            hide_number BOOLEAN NOT NULL,
            enable_location BOOLEAN NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('Landing_Page.html')

@app.route('/onboarding.html')
def onboarding():
    return render_template('onboarding.html')

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    name = request.form.get('name')
    phone = request.form.get('phone')
    whatsapp = request.form.get('whatsapp')
    
    # ضبط رقم الواتساب
    whatsapp = whatsapp.replace(' ', '').replace('+', '')
    if whatsapp.startswith('0'):
        whatsapp = '20' + whatsapp[1:]
    elif not whatsapp.startswith('20'):
         whatsapp = '20' + whatsapp
    
    hide_number = True if request.form.get('hide_number') == 'on' else False
    enable_location = True if request.form.get('enable_location') == 'on' else False
    
    user_id = uuid.uuid4().hex[:8]
    finder_link = f"{request.host_url}finder/{user_id}"
    
    # توليد وحفظ الصورة في المسار الإجباري
    qr = qrcode.make(finder_link)
    image_name = f"{user_id}.png"
    image_path = os.path.join(QR_FOLDER, image_name)
    qr.save(image_path)
    
    # حفظ بيانات العميل
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, name, phone, whatsapp, hide_number, enable_location)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, phone, whatsapp, hide_number, enable_location))
    conn.commit()
    conn.close()
    
    return render_template('success.html', name=name)

@app.route('/finder/<user_id>')
def finder(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('Finder_Page.html', 
                               owner_name=user[2],
                               owner_phone=user[3],
                               owner_whatsapp=user[4],
                               hide_number=user[5],
                               enable_location=user[6],
                               owner_id=user_id)
    else:
        return "هذا الـ QR Code غير صالح أو تم حذفه."

@app.route('/admin')
def admin_panel():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id DESC')
    orders = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', orders=orders)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)