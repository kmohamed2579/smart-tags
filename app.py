from flask import Flask, render_template, request
import qrcode
import os
import uuid
import sqlite3 # المكتبة الخاصة بقاعدة البيانات

app = Flask(__name__)
os.makedirs('static/qrcodes', exist_ok=True)

# 1. دالة لإنشاء قاعدة البيانات والجدول (بتشتغل أول ما السيرفر يقوم)
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # بنعمل جدول اسمه users لو مش موجود
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

# بننادي على الدالة عشان تجهز الجدول
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
    
    # --- الكود الجديد لضبط رقم الواتساب ---
    # بنشيل أي مسافات أو علامات + اليوزر ممكن يكون كتبها بالغلط
    whatsapp = whatsapp.replace(' ', '').replace('+', '')
    
    # لو الرقم بيبدأ بـ 0 (زي 010 أو 011)، بنشيل الصفر وبنحط مكانه 20
    if whatsapp.startswith('0'):
        whatsapp = '20' + whatsapp[1:]
    # لو الرقم مش بيبدأ بـ 20 أساساً، بنضيفها
    elif not whatsapp.startswith('20'):
         whatsapp = '20' + whatsapp
    # ----------------------------------------
    
    # تحويل اختيارات الخصوصية لـ True أو False
    hide_number = True if request.form.get('hide_number') == 'on' else False
    enable_location = True if request.form.get('enable_location') == 'on' else False
    
    user_id = uuid.uuid4().hex[:8]
    finder_link = f"{request.host_url}finder/{user_id}"
    
    qr = qrcode.make(finder_link)
    image_name = f"{user_id}.png"
    image_path = os.path.join('static', 'qrcodes', image_name)
    qr.save(image_path)
    
    # 2. حفظ بيانات العميل الجديد في قاعدة البيانات
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, name, phone, whatsapp, hide_number, enable_location)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, phone, whatsapp, hide_number, enable_location))
    conn.commit()
    conn.close()
    
    return render_template('success.html', name=name)

# 3. مسار المكتشف (دلوقتي بيسحب داتا حقيقية من الداتا بيز)
@app.route('/finder/<user_id>')
def finder(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # بندور على العميل باستخدام الـ user_id بتاعه
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    # لو العميل موجود، هنبعت بياناته الحقيقية لصفحة الـ HTML
    if user:
        return render_template('Finder_Page.html', 
                               owner_name=user[2],        # الاسم
                               owner_phone=user[3],       # التليفون
                               owner_whatsapp=user[4],    # الواتساب
                               hide_number=user[5],       # إخفاء الرقم
                               enable_location=user[6],   # التنبيه بالمكان
                               owner_id=user_id)
    else:
        return "هذا الـ QR Code غير صالح أو تم حذفه."

# ==========================================
# لوحة التحكم السرية للمدير (Admin Dashboard)
# ==========================================
@app.route('/admin')
def admin_panel():
    # بنفتح الداتا بيز ونجيب كل الأوردرات مترتبة من الأحدث للأقدم
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id DESC')
    orders = cursor.fetchall()
    conn.close()
    
    # بنبعت الأوردرات لصفحة الأدمن عشان تعرضها
    return render_template('admin.html', orders=orders)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)