from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import random
import datetime
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta 

app = Flask(__name__)
# Tạo thư mục chứa ảnh upload nếu chưa có
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
CORS(app)

# --- CẤU HÌNH KẾT NỐI MYSQL ---
DB_USER = 'root'
DB_PASSWORD = '123456' # Điền mật khẩu MySQL của bạn
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'ntdvhome_db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class User(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    default_address = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))

class Service(db.Model):
    __tablename__ = 'Services'
    service_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Numeric(10, 2))
    icon_url = db.Column(db.String(255))

class Provider(db.Model):
    __tablename__ = 'Providers'
    provider_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    cccd_number = db.Column(db.String(20), unique=True, nullable=False)
    avatar_url = db.Column(db.String(255))
    evidence_url = db.Column(db.String(255))
    bio_description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='inactive') # inactive, active, banned
    balance = db.Column(db.Numeric(10, 2), default=0)

class Booking(db.Model):
    __tablename__ = 'Bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('Providers.provider_id'), nullable=True) # Có thể null lúc mới đặt (chưa có thợ)
    service_id = db.Column(db.Integer, db.ForeignKey('Services.service_id'))
    
    # Thêm 2 cột này để lưu Gói và Giá tiền
    package_name = db.Column(db.String(100)) 
    total_amount = db.Column(db.Numeric(10, 2))
    
    service_address = db.Column(db.Text, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, accepted, in_progress, completed, cancelled

# --- CẬP NHẬT MODEL REVIEW ---
class Review(db.Model):
    __tablename__ = 'Reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('Bookings.booking_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    # Thêm dòng này để khớp với cấu trúc Database của bạn
    provider_id = db.Column(db.Integer, db.ForeignKey('Providers.provider_id'), nullable=True) 
    rating_star = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

# --- 1. THÊM BẢNG LƯU TIN NHẮN (Khai báo dưới bảng Booking) ---
from datetime import datetime # Nhớ thêm dòng này ở tuốt trên cùng file nếu chưa có

# BẢNG LƯU TRỮ TIN NHẮN
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, nullable=False)
    sender_type = db.Column(db.String(20)) # Phân biệt 'customer' (khách) hoặc 'provider' (thợ)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# BẢNG LƯU TRỮ TIN NHẮN TRỰC TIẾP GIỮA NGƯỜI DÙNG VỚI NHAU
class DirectMessage(db.Model):
    __tablename__ = 'DirectMessages'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_dms')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_dms')

# --- THÊM BẢNG lịch sử giao dịch: ---
# Cập nhật bảng Provider trong app.py

# Tạo thêm bảng Lịch sử ví để thợ theo dõi
class WalletTransaction(db.Model):
    __tablename__ = 'WalletTransactions'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('Providers.provider_id'))
    amount = db.Column(db.Numeric(10, 2)) # Số tiền biến động (+ nạp tiền, - trừ phí)
    transaction_type = db.Column(db.String(20)) # 'deposit' hoặc 'fee'
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- BẢNG BÀI ĐĂNG CỘNG ĐỒNG ---
class Post(db.Model):
    __tablename__ = 'Posts'
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    content = db.Column(db.Text)
    media_url = db.Column(db.String(500))
    media_type = db.Column(db.String(10))  # 'image' hoặc 'video'
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', foreign_keys=[user_id], backref='posts')

# --- BẢNG BÌNH LUẬN BÀI ĐĂNG ---
class PostComment(db.Model):
    __tablename__ = 'PostComments'
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('Posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', foreign_keys=[user_id], backref='comments')

# Bảng mới cho Quảng cáo & Đề xuất thợ uy tín
class FeaturedProvider(db.Model):
    __tablename__ = 'FeaturedProviders'
    id = db.Column(db.Integer, primary_key=True)
    badge = db.Column(db.String(50)) # VD: '🔥 Nổi bật', '⭐ Quảng cáo'
    avatar_icon = db.Column(db.String(255)) # Emoji hoặc URL
    provider_name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    rating = db.Column(db.Float, default=5.0)
    review_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(255)) # Cách nhau bởi dấu phẩy
    price_text = db.Column(db.String(100))
    service_link = db.Column(db.String(255))

# Lưu trữ OTP tạm thời (Key là email)
otp_storage = {}

# ==========================================
# CÁC ROUTE ĐIỀU HƯỚNG GIAO DIỆN
# ==========================================

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login')
def login_page():
    return render_template('login.html') 

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/register')
def register_page():
    return render_template('register.html') 

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot-password.html') 

@app.route('/service-detail')
def service_detail_page():
    return render_template('service-detail.html')


# ==========================================
# 2. CÁC API XỬ LÝ DỮ LIỆU (BACKEND)
# ==========================================

# --- API ĐĂNG KÝ ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    existing = User.query.filter((User.phone_number == data['phone']) | (User.email == data['email'])).first()
    if existing:
        return jsonify({"message": "Số điện thoại hoặc Email đã được đăng ký!"}), 400

    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(
        full_name=data['fullName'],
        phone_number=data['phone'],
        email=data['email'],
        password_hash=hashed_pw
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Đăng ký thành công!"}), 201

# --- API ĐĂNG NHẬP ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    # Frontend gửi email hoặc phone tùy thuộc vào file login.html
    user = User.query.filter((User.email == data.get('email')) | (User.phone_number == data.get('phone'))).first()
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({
                "token": "fake-jwt-token",
                "user": {
                    "id": user.user_id,  # <-- THÊM DÒNG NÀY
                    "email": user.email, # <-- THÊM DÒNG NÀY
                    "name": user.full_name,
                    "fullName": user.full_name,
                    "phone": user.phone_number,
                    "role": user.role
                }
        }), 200
    return jsonify({"message": "Thông tin đăng nhập không chính xác!"}), 401

# --- CẤU HÌNH GỬI EMAIL ---
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cấu hình email của bạn
SENDER_EMAIL = "lenlao570@gmail.com" # Email có mật khẩu ứng dụng
SENDER_PASSWORD = "raqvoaszjkdmjqlv" # Mật khẩu ứng dụng mới (đã xóa khoảng trắng)

def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "Mã xác nhận OTP - Khôi phục mật khẩu NTDVhome"

        body = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
                    <h2 style="color: #0f52ba; text-align: center;">Khôi phục mật khẩu</h2>
                    <p>Xin chào,</p>
                    <p>Bạn đã yêu cầu khôi phục mật khẩu cho tài khoản tại NTDVhome. Đây là mã OTP xác nhận của bạn:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #ff6b35; background: #fff7ed; padding: 15px 30px; border-radius: 8px; border: 2px dashed #fed7aa;">{otp}</span>
                    </div>
                    <p>Mã OTP này có hiệu lực trong vòng <strong>5 phút</strong>. Vui lòng không chia sẻ mã này cho bất kỳ ai.</p>
                    <p style="color: #64748b; font-size: 12px; text-align: center; margin-top: 40px;">Đội ngũ hỗ trợ NTDVhome</p>
                </div>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        return False

# --- API QUÊN MẬT KHẨU (BƯỚC 1: GỬI OTP) ---
@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email không tồn tại trong hệ thống!"}), 404
    
    otp = str(random.randint(100000, 999999))
    # SỬA LỖI DATETIME BỊ SAI CÚ PHÁP
    otp_storage[email] = {
        "otp": otp,
        "expires": datetime.now() + timedelta(minutes=5)
    }
    
    # Gửi mail thật
    success = send_otp_email(email, otp)
    if success:
        return jsonify({"message": "Mã OTP đã được gửi thành công!"}), 200
    else:
        return jsonify({"message": "Lỗi khi gửi email, vui lòng thử lại sau!"}), 500

# --- API XÁC THỰC OTP (BƯỚC 2) ---
@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email, otp_in = data.get('email'), data.get('otp')
    stored = otp_storage.get(email)
    
    if not stored:
        return jsonify({"message": "Không tìm thấy yêu cầu OTP cho email này!"}), 400
        
    if datetime.now() > stored['expires']:
        return jsonify({"message": "Mã OTP đã hết hạn, vui lòng gửi lại!"}), 400
        
    if stored['otp'] != otp_in:
        return jsonify({"message": "Mã OTP không chính xác!"}), 400
        
    return jsonify({"message": "Xác thực OTP thành công!"}), 200

# --- API ĐẶT LẠI MẬT KHẨU (BƯỚC 3) ---
@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email, new_pw = data.get('email'), data.get('newPassword')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Lỗi không xác định!"}), 404

    hashed_pw = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password_hash = hashed_pw
    db.session.commit()
    if email in otp_storage: del otp_storage[email]
    return jsonify({"message": "Đổi mật khẩu thành công!"}), 200

# --- API ĐỔI MẬT KHẨU TẠI TRANG CÁ NHÂN ---
@app.route('/api/user/<int:user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    data = request.json
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not old_password or not new_password:
        return jsonify({"message": "Vui lòng nhập đầy đủ mật khẩu cũ và mới!"}), 400

    # 1. Tìm người dùng
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Không tìm thấy tài khoản!"}), 404

    # 2. Kiểm tra mật khẩu cũ xem có khớp không
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"message": "Mật khẩu hiện tại không chính xác!"}), 401

    # 3. Băm mật khẩu mới và lưu vào Database
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password_hash = hashed_pw
    db.session.commit()

    return jsonify({"message": "Đổi mật khẩu thành công!"}), 200

# --- API THÊM DỊCH VỤ MỚI ---
@app.route('/api/admin/services', methods=['POST'])
def add_service():
    data = request.json
    new_svc = Service(
        service_name=data['name'],
        description=data.get('description', ''),
        base_price=data['price'],
        icon_url=data.get('icon', '🛠️')
    )
    db.session.add(new_svc)
    db.session.commit()
    return jsonify({"message": "Thêm dịch vụ thành công!"}), 201

# --- API XÓA DỊCH VỤ ---
@app.route('/api/admin/services/<int:id>', methods=['DELETE'])
def delete_service(id):
    svc = Service.query.get(id)
    if not svc:
        return jsonify({"message": "Không tìm thấy dịch vụ!"}), 404
    db.session.delete(svc)
    db.session.commit()
    return jsonify({"message": "Đã xóa dịch vụ thành công!"}), 200

# --- API SỬA DỊCH VỤ ---
@app.route('/api/admin/services/<int:id>', methods=['PUT'])
def update_service(id):
    svc = Service.query.get(id)
    if not svc:
        return jsonify({"message": "Không tìm thấy dịch vụ!"}), 404
    
    data = request.json
    svc.service_name = data['name']
    svc.description = data.get('description', '')
    svc.base_price = data['price']
    svc.icon_url = data.get('icon', '🛠️')
    
    db.session.commit()
    return jsonify({"message": "Cập nhật dịch vụ thành công!"}), 200

# --- API DỊCH VỤ ---
@app.route('/api/services', methods=['GET'])
def get_services():
    services = Service.query.all()
    return jsonify([{
        "service_id": s.service_id,
        "name": s.service_name,
        "description": s.description,
        "price_range": str(s.base_price), # Khớp với price_range trong index.html/service-detail.html
        "icon": s.icon_url
    } for s in services])

# --- API  NGƯỜI DÙNG ---
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # Lấy toàn bộ người dùng từ Database
    users = User.query.all()
    return jsonify([{
        "user_id": u.user_id,
        "full_name": u.full_name,
        "phone_number": u.phone_number,
        "email": u.email,
        "role": u.role
    } for u in users]), 200

# --- API THAY ĐỔI QUYỀN (ROLE) NGƯỜI DÙNG ---
@app.route('/api/admin/users/<int:id>/role', methods=['PUT'])
def update_user_role(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng!"}), 404
    
    data = request.json
    user.role = data.get('role', 'user') # Nhận role mới từ frontend
    db.session.commit()
    return jsonify({"message": f"Đã cập nhật quyền thành {user.role}!"}), 200

# --- API XÓA NGƯỜI DÙNG ---
@app.route('/api/admin/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng!"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Đã xóa người dùng thành công!"}), 200

# --- QUẢN LÝ ĐƠN HÀNG (BOOKINGS) ---
@app.route('/api/admin/bookings', methods=['GET'])
def admin_get_bookings():
    bookings = db.session.query(Booking, User, Service, Provider)\
        .join(User, Booking.user_id == User.user_id)\
        .join(Service, Booking.service_id == Service.service_id)\
        .outerjoin(Provider, Booking.provider_id == Provider.provider_id).all()
    
    result = []
    for b, u, s, p in bookings:
        result.append({
            "id": b.booking_id,
            "customer": u.full_name,
            "service": s.service_name,
            "address": b.service_address,
            "time": b.scheduled_time.strftime('%d/%m/%Y %H:%M'),
            "status": b.status,
            "provider": p.full_name if p else "Chưa phân công"
        })
    return jsonify(result)

# --- THỐNG KÊ TỔNG QUAN DASHBOARD ---
from sqlalchemy.sql import func

@app.route('/api/admin/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    # Tổng thợ (đã duyệt)
    total_providers = Provider.query.filter_by(is_verified=True).count()
    
    # Doanh thu (Ví dụ: Tính 20% chiết khấu từ các đơn hoàn thành)
    # Giả sử giá trị đơn hàng nằm ở total_amount hoặc price, trong Booking model của bạn chỉ có price/total_amount.
    # Ta sẽ tính tổng price của các booking có status 'completed'
    completed_bookings = Booking.query.filter_by(status='completed').all()
    total_revenue = 0
    for b in completed_bookings:
        # Nếu model có total_amount
        if hasattr(b, 'total_amount') and b.total_amount:
            total_revenue += float(b.total_amount) * 0.20 # 20% chiết khấu
        # Nếu model dùng price (trong API có thể là price)
        elif hasattr(b, 'price') and b.price:
            total_revenue += float(b.price) * 0.20
            
    # Thợ đánh giá cao (Ví dụ rating >= 4.0) - Cần join với bảng Review
    # Vì đơn giản, lấy số lượng đánh giá 5 sao
    five_star_reviews = Review.query.filter_by(rating_star=5).count()
    bad_reviews = Review.query.filter(Review.rating_star <= 2).count()

    return jsonify({
        "total_providers": total_providers,
        "total_revenue": total_revenue,
        "five_star_reviews": five_star_reviews,
        "bad_reviews": bad_reviews
    })

# --- API GỬI VÀ NHẬN TIN NHẮN ---
@app.route('/api/bookings/<int:booking_id>/chat', methods=['GET', 'POST'])
def handle_chat(booking_id):
    if request.method == 'POST':
        data = request.json
        if not data or 'message' not in data or 'sender_type' not in data:
            return jsonify({"message": "Thiếu dữ liệu"}), 400

        new_msg = ChatMessage(
            booking_id=booking_id,
            sender_type=data['sender_type'],
            message=data['message']
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({"message": "Đã gửi"}), 201

    if request.method == 'GET':
        messages = ChatMessage.query.filter_by(booking_id=booking_id).order_by(ChatMessage.created_at).all()
        return jsonify([{
            "id": m.id,
            "sender_type": m.sender_type,
            "message": m.message,
            "time": m.created_at.strftime('%H:%M')
        } for m in messages]), 200

# ==========================================
# API NHẮN TIN TRỰC TIẾP (DIRECT MESSAGING)
# ==========================================
from sqlalchemy import or_

@app.route('/api/chat/<int:user_id>/conversations', methods=['GET'])
def get_conversations(user_id):
    try:
        messages = DirectMessage.query.filter(
            or_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == user_id)
        ).order_by(DirectMessage.created_at.desc()).all()

        conversation_map = {}
        for msg in messages:
            other_user = msg.receiver if msg.sender_id == user_id else msg.sender
            if not other_user:
                continue
                
            other_id = other_user.user_id
            if other_id not in conversation_map:
                conversation_map[other_id] = {
                    "user_id": other_id,
                    "name": other_user.full_name,
                    "last_message": msg.message_text,
                    "last_time": msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else None
                }

        return jsonify(list(conversation_map.values())), 200
    except Exception as e:
        print("Lỗi lấy danh sách chat:", e)
        return jsonify({"message": "Lỗi Server"}), 500

@app.route('/api/chat/<int:user_id>/history/<int:other_id>', methods=['GET'])
def get_chat_history(user_id, other_id):
    try:
        messages = DirectMessage.query.filter(
            or_(
                (DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == other_id),
                (DirectMessage.sender_id == other_id) & (DirectMessage.receiver_id == user_id)
            )
        ).order_by(DirectMessage.created_at.asc()).all()

        return jsonify([{
            "id": m.message_id,
            "text": m.message_text,
            "is_mine": m.sender_id == user_id,
            "time": m.created_at.strftime('%Y-%m-%d %H:%M:%S') if m.created_at else None
        } for m in messages]), 200
    except Exception as e:
        print("Lỗi lấy lịch sử chat:", e)
        return jsonify({"message": "Lỗi Server"}), 500

@app.route('/api/chat/send', methods=['POST'])
def send_direct_message():
    try:
        data = request.json
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        text = data.get('text')

        if not sender_id or not receiver_id or not text:
            return jsonify({"message": "Thiếu thông tin gửi."}), 400

        new_msg = DirectMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_text=text
        )
        db.session.add(new_msg)
        db.session.commit()

        return jsonify({
            "message": "Đã gửi", 
            "msg": {
                "id": new_msg.message_id,
                "text": new_msg.message_text,
                "is_mine": True,
                "time": new_msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if new_msg.created_at else None
            }
        }), 201
    except Exception as e:
        print("Lỗi gửi tin nhắn:", e)
        db.session.rollback()
        return jsonify({"message": "Lỗi Server"}), 500

# --- QUẢN LÝ ĐỐI TÁC / THỢ ---
@app.route('/api/admin/providers', methods=['GET'])
def admin_get_providers():
    providers = Provider.query.all()
    return jsonify([{
        "id": p.provider_id, 
        "name": p.full_name, 
        "phone": p.phone_number, 
        "cccd": p.cccd_number, 
        "bio": p.bio_description,  # Lấy thêm Kinh nghiệm
        "avatar": p.avatar_url,    # Lấy thêm Link ảnh
        "verified": p.is_verified, 
        "status": p.status
    } for p in providers])

@app.route('/api/admin/providers/<int:id>/status', methods=['PUT'])
def admin_update_provider(id):
    p = Provider.query.get(id)
    data = request.json
    if 'status' in data: p.status = data['status']
    if 'verified' in data: p.is_verified = data['verified']
    db.session.commit()
    return jsonify({"message": "Đã cập nhật thợ!"})

# --- QUẢN LÝ ĐÁNH GIÁ ---
@app.route('/api/admin/reviews', methods=['GET'])
def admin_get_reviews():
    reviews = db.session.query(Review, User).join(User, Review.user_id == User.user_id).all()
    return jsonify([{"id": r.review_id, "customer": u.full_name, "stars": r.rating_star, "comment": r.comment} for r, u in reviews])

@app.route('/api/admin/reviews/<int:id>', methods=['DELETE'])
def admin_delete_review(id):
    r = Review.query.get(id)
    if r: db.session.delete(r); db.session.commit()
    return jsonify({"message": "Đã xóa đánh giá!"})

# --- TRANG CHI TIẾT THỢ VÀ ĐÁNH GIÁ (PUBLIC) ---
@app.route('/provider-detail')
def provider_detail_page():
    return render_template('provider-detail.html')

@app.route('/api/public/providers/<int:id>', methods=['GET'])
def get_public_provider(id):
    p = Provider.query.get(id)
    if not p: return jsonify({"message": "Không tìm thấy thợ"}), 404
    
    # Tính điểm đánh giá trung bình
    reviews = Review.query.filter_by(provider_id=id).all()
    avg_rating = sum(r.rating_star for r in reviews) / len(reviews) if reviews else 5.0
    
    return jsonify({
        "id": p.provider_id,
        "name": p.full_name,
        "bio": p.bio_description or "Chưa có giới thiệu",
        "avatar": p.avatar_url or "👷",
        "verified": p.is_verified,
        "avg_rating": round(avg_rating, 1),
        "review_count": len(reviews)
    }), 200

@app.route('/api/public/providers/<int:id>/reviews', methods=['GET'])
def get_public_provider_reviews(id):
    reviews = db.session.query(Review, User).join(User, Review.user_id == User.user_id).filter(Review.provider_id == id).order_by(Review.review_id.desc()).all()
    return jsonify([{
        "customer": u.full_name,
        "stars": r.rating_star,
        "comment": r.comment or "Không có bình luận"
    } for r, u in reviews]), 200

# --- ROUTE MỞ TRANG CÁ NHÂN ---
@app.route('/profile')
def user_profile_page():
    return render_template('profile.html')

# --- ROUTE CỘNG ĐỒNG ---
@app.route('/community')
def community_page():
    return render_template('community.html')

# --- ROUTE CHAT TRỰC TIẾP ---
@app.route('/chat')
def chat_page():
    return render_template('chat.html')

# --- ROUTE HỒ SƠ CÔNG KHAI NGƯỜI DÙNG ---
@app.route('/user-profile/<int:user_id>')
def public_user_profile_page(user_id):
    return render_template('user-profile.html')

# --- ROUTE LỊCH SỬ ĐƠN HÀNG CỦA TÔI ---
@app.route('/my-orders')
def my_orders_page():
    return render_template('myorders.html')

# --- SỬA LẠI API LẤY THÔNG TIN CÁ NHÂN (Thêm thông tin thợ) ---
# --- CẬP NHẬT API LẤY THÔNG TIN CÁ NHÂN ---
@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404
        
    provider = Provider.query.filter_by(phone_number=user.phone_number).first()
    
    # CHỈ COI LÀ THỢ NẾU HỒ SƠ TỒN TẠI VÀ CHƯA NGHỈ HƯU
    is_active_provider = False
    bio_text = ""
    
    if provider and provider.status != 'inactive':
        is_active_provider = True
        bio_text = provider.bio_description
    
    return jsonify({
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "email": user.email,
        "default_address": user.default_address or "",
        "is_provider": is_active_provider, # Trả về False nếu đã nghỉ
        "bio": bio_text,
        "avatar_url": user.avatar_url or ""
    })

# --- THÊM MỚI API: USER CẬP NHẬT AVATAR ---
@app.route('/api/user/<int:user_id>/avatar', methods=['POST'])
def update_avatar(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404

    if 'avatar' not in request.files:
        return jsonify({"message": "Không tìm thấy file ảnh!"}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"message": "Không có ảnh nào được chọn!"}), 400

    filename = secure_filename(file.filename)
    safe_filename = f"avatar_{user_id}_{filename}"
    filepath = os.path.join('static', 'uploads', safe_filename)
    file.save(filepath)
    avatar_url = f"/static/uploads/{safe_filename}"

    user.avatar_url = avatar_url
    
    # Nếu là thợ, cập nhật luôn ảnh của thợ
    provider = Provider.query.filter_by(phone_number=user.phone_number).first()
    if provider:
        provider.avatar_url = avatar_url

    db.session.commit()
    return jsonify({"message": "✅ Cập nhật ảnh đại diện thành công!", "avatar_url": avatar_url}), 200

# --- THÊM MỚI API: THỢ CẬP NHẬT KINH NGHIỆM ---
@app.route('/api/user/<int:user_id>/update-bio', methods=['PUT'])
def update_provider_bio(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404
        
    provider = Provider.query.filter_by(phone_number=user.phone_number).first()
    if not provider:
        return jsonify({"message": "Bạn chưa đăng ký làm thợ!"}), 400
        
    data = request.json
    provider.bio_description = data.get('bio', '')
    db.session.commit()
    
    return jsonify({"message": "✅ Đã cập nhật kinh nghiệm thành công!"}), 200

# --- API LẤY LỊCH SỬ ĐƠN HÀNG CỦA RIÊNG USER ĐÓ ---
@app.route('/api/user/<int:user_id>/bookings', methods=['GET'])
def get_user_bookings(user_id):
    bookings = db.session.query(Booking, Service, Provider)\
        .join(Service, Booking.service_id == Service.service_id)\
        .outerjoin(Provider, Booking.provider_id == Provider.provider_id)\
        .filter(Booking.user_id == user_id)\
        .order_by(Booking.booking_id.desc()).all()
    
    result = []
    for b, s, p in bookings:
        result.append({
            "id": b.booking_id,
            "service": s.service_name,
            "time": b.scheduled_time.strftime('%d/%m/%Y %H:%M'),
            "address": b.service_address,
            "status": b.status,
            "total": str(b.total_amount),
            "provider": p.full_name if p else "Đang tìm thợ"
        })
    return jsonify(result)

# --- API ĐĂNG KÝ TRỞ THÀNH THỢ ---
@app.route('/api/user/<int:user_id>/register-provider', methods=['POST'])
def register_provider(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404
    
    # Đổi từ request.json sang request.form vì có kèm theo File upload
    cccd = request.form.get('cccd')
    bio = request.form.get('bio')
    
    # Xử lý lưu ảnh BẰNG CHỨNG (CCCD/Bằng cấp)
    evidence_url = None
    if 'evidence_image' in request.files:
        file = request.files['evidence_image']
        if file.filename != '':
            filename = secure_filename(file.filename)
            safe_filename = f"evidence_{user_id}_{filename}"
            filepath = os.path.join('static', 'uploads', safe_filename)
            file.save(filepath)
            evidence_url = f"/static/uploads/{safe_filename}"
    
    existing_provider = Provider.query.filter(
        (Provider.phone_number == user.phone_number) | (Provider.cccd_number == cccd)
    ).first()
    
    # --- LOGIC XỬ LÝ NẾU ĐÃ CÓ HỒ SƠ TỪ TRƯỚC ---
    if existing_provider:
        # Nếu thợ đang ở trạng thái nghỉ hưu ('inactive') -> Cho phép đi làm lại
        if existing_provider.status == 'inactive':
            existing_provider.cccd_number = cccd
            existing_provider.bio_description = bio
            if evidence_url: 
                existing_provider.evidence_url = evidence_url 
            
            # Đổi trạng thái về chờ duyệt
            existing_provider.is_verified = False
            existing_provider.status = 'pending'
            
            db.session.commit()
            return jsonify({"message": "Hồ sơ xin đi làm lại đã được gửi! Vui lòng chờ Admin duyệt."}), 200
        else:
            # Nếu đang làm thợ bình thường hoặc đang chờ duyệt
            return jsonify({"message": "Tài khoản hoặc CCCD này đang là đối tác hoặc đơn đang chờ duyệt!"}), 400
            
    # --- NẾU LÀ TÂN BINH CHƯA TỪNG LÀM THỢ ---
    new_provider = Provider(
        full_name=user.full_name,
        phone_number=user.phone_number,
        cccd_number=cccd,
        bio_description=bio,
        evidence_url=evidence_url, # Lưu ảnh bằng chứng
        avatar_url=user.avatar_url, # Lấy avatar từ tài khoản user sang
        is_verified=False,
        status='pending' 
    )
    db.session.add(new_provider)
    db.session.commit()
    
    return jsonify({"message": "Gửi hồ sơ và ảnh minh chứng thành công! Vui lòng chờ Admin duyệt."}), 201

# --- API: THỢ HỦY TƯ CÁCH ĐỐI TÁC (XIN NGHỈ) ---
@app.route('/api/user/<int:user_id>/deactivate-provider', methods=['PUT'])
def deactivate_provider(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng"}), 404
        
    provider = Provider.query.filter_by(phone_number=user.phone_number).first()
    if not provider:
        return jsonify({"message": "Bạn chưa phải là thợ!"}), 400
        
    # Chuyển trạng thái sang ngưng hoạt động và gỡ xác minh (để đá khỏi danh sách API)
    provider.status = 'inactive'
    provider.is_verified = False
    
    db.session.commit()
    
    return jsonify({"message": "Đã hủy tư cách đối tác thành công. Cảm ơn bạn đã đồng hành!"}), 200
# ==========================================
# 3. API LUỒNG ĐẶT LỊCH & XỬ LÝ ĐƠN HÀNG (GRAB-STYLE)
# ==========================================
from datetime import datetime

# --- 1. KHÁCH HÀNG ĐẶT LỊCH MỚI ---
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    
    # Chuyển đổi chuỗi ngày giờ từ Frontend sang chuẩn datetime của Python
    try:
        dt_string = f"{data['date']} {data['time']}"
        scheduled_dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M')
    except:
        scheduled_dt = datetime.now() # Fallback nếu chọn "Đặt ngay"
        
    new_booking = Booking(
        user_id=data['user_id'],
        service_id=data['service_id'],
        provider_id=data.get('provider_id'), # Bằng Null nếu hệ thống tự tìm thợ
        package_name=data.get('package_name', 'Tiêu chuẩn'),
        total_amount=data.get('total_price', 0),
        service_address=data['address'],
        scheduled_time=scheduled_dt,
        status='pending'
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({
        "message": "Đặt lịch thành công!", 
        "booking_id": new_booking.booking_id
    }), 201

# --- 2. LẤY CHI TIẾT ĐƠN HÀNG (CHO TRANG BOOKING.HTML CỦA KHÁCH) ---
# --- API LẤY CHI TIẾT 1 ĐƠN HÀNG (ĐÃ FIX LỖI TÊN CỘT) ---
@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_single_booking(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"message": "Không tìm thấy đơn hàng"}), 404

        # Lấy thông tin dịch vụ
        service_id = getattr(booking, 'service_id', None)
        service = Service.query.get(service_id) if service_id else None
        
        # Lấy thông tin thợ
        provider_id = getattr(booking, 'provider_id', None)
        provider = Provider.query.get(provider_id) if provider_id else None

        provider_data = None
        if provider:
            provider_data = {
                # ĐÃ SỬA: Xóa bỏ provider.id gây lỗi, thay bằng chuỗi rỗng
                "id": getattr(provider, 'provider_id', ''), 
                "name": getattr(provider, 'full_name', ''),
                "phone": getattr(provider, 'phone_number', ''),
                "avatar": getattr(provider, 'avatar_url', ''),
                "bio": getattr(provider, 'bio_description', '')
            }

        # Xử lý ngày tháng an toàn (dùng scheduled_time cho đúng model)
        scheduled = getattr(booking, 'scheduled_time', None)
        b_date = scheduled.strftime('%Y-%m-%d') if scheduled else ''
        b_time = scheduled.strftime('%H:%M') if scheduled else ''
            
        return jsonify({
            "id": getattr(booking, 'booking_id', booking_id),
            "status": getattr(booking, 'status', 'pending'),
            "service_name": getattr(service, 'service_name', 'Dịch vụ'),
            "package_name": getattr(booking, 'package_name', ''),
            "total_price": float(booking.total_amount) if booking.total_amount else 0,
            "address": getattr(booking, 'service_address', ''),
            "date": b_date,
            "time": b_time,
            "provider": provider_data
        }), 200

    except Exception as e:
        print("======== LỖI BACKEND TẠI API LẤY ĐƠN HÀNG ========")
        print(str(e))
        return jsonify({"message": f"Lỗi Server: {str(e)}"}), 500

# --- 3. LẤY DANH SÁCH ĐƠN HÀNG CHO THỢ (WORKERORDERS.HTML) ---
@app.route('/api/provider/<int:provider_id>/orders', methods=['GET'])
def get_provider_orders(provider_id):
    # Lấy các đơn được giao cho thợ này
    bookings = Booking.query.filter_by(provider_id=provider_id).order_by(Booking.scheduled_time.asc()).all()
    
    result = []
    for b in bookings:
        user = User.query.get(b.user_id)
        service = Service.query.get(b.service_id)
        result.append({
            "id": b.booking_id,
            "customer_name": user.full_name,
            "customer_phone": user.phone_number,
            "service_name": service.service_name,
            "package_name": b.package_name,
            "address": b.service_address,
            "time": b.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            "status": b.status,
            "price": str(b.total_amount)
        })
    return jsonify(result), 200

# --- CÁC ROUTE MỚI THÊM VÀO ---

@app.route('/service/cleaning')
def service_cleaning_page():
    # Trỏ đến file Servicecleaning.html của bạn
    return render_template('Servicecleaning.html')

@app.route('/service/electric')
def service_electric_page():
    return render_template('Serviceelectric.html')

@app.route('/service/aircon')
def service_aircon_page():
    return render_template('Serviceaircon.html')

@app.route('/booking')
def booking_page():
    # Lưu ý: File của bạn đang có khoảng trắng ở tên là "Booking.html"
    # Bạn nên đổi tên file thành "Booking.html" cho chuẩn, nếu không thì code phải để y hệt như dưới:
    return render_template('Booking.html') 
def booking_tracking_page():
    return render_template('Booking.html')

# --- CÁC TRANG CỦA KÊNH THỢ ---

@app.route('/worker/orders')    
def worker_orders_page():
    # Trỏ đến trang quản lý đơn của thợ
    return render_template('Workerorders.html')
@app.route('/worker/location')
def worker_location_page():
    return render_template('Workerlocation.html')

@app.route('/worker/income')
def worker_income_page():
    return render_template('Workerincome.html')

@app.route('/worker/reviews')
def worker_reviews_page():
    return render_template('Workerreviews.html')

@app.route('/worker/notifications')
def worker_notifications_page():
    return render_template('Workernotifications.html')

@app.route('/worker/settings')
def worker_settings_page():
    return render_template('Workersettings.html')

# --- API LẤY DANH SÁCH THỢ THEO TỪNG DỊCH VỤ ---
@app.route('/api/providers/active', methods=['GET'])
def get_active_providers():
    # Lấy tham số 'service' từ trên thanh URL (ví dụ: ?service=cleaning)
    service_type = request.args.get('service', '').lower()
    
    # Kéo toàn bộ thợ đã duyệt
    providers = Provider.query.filter_by(is_verified=True, status='active').all()
    
    result = []
    for p in providers:
        bio = (p.bio_description or "").lower() # Lấy phần giới thiệu bản thân của thợ
        
        # BỘ LỌC TỪ KHÓA THÔNG MINH
        if service_type == 'cleaning' and not any(word in bio for word in ['dọn', 'vệ sinh', 'sạch', 'giặt']):
            continue # Nếu đang tìm thợ dọn dẹp mà bio không có chữ 'dọn', bỏ qua!
            
        if service_type == 'electric' and not any(word in bio for word in ['điện', 'nước', 'ống', 'lắp']):
            continue # Tương tự với thợ điện nước
            
        if service_type == 'aircon' and not any(word in bio for word in ['lạnh', 'điều hòa', 'điều hoà', 'gas']):
            continue # Tương tự với thợ máy lạnh
            
        # Nếu vượt qua được bộ lọc trên, thêm thợ này vào danh sách hiển thị
        result.append({
            "id": p.provider_id,
            "name": p.full_name,
            "bio": p.bio_description if p.bio_description else "Thợ chuyên nghiệp",
            "avatar": p.avatar_url,
            "reviews": random.randint(10, 150),
            "distance": round(random.uniform(0.5, 5.0), 1)
        })
        
    return jsonify(result), 200

# Ví dụ logic kiểm tra trong API nhận đơn
@app.route('/api/bookings/<int:booking_id>/accept', methods=['PUT'])
def accept_booking(booking_id):
    data = request.json
    provider_id = data.get('provider_id')
    
    # 1. Lấy thông tin đơn hàng mới định nhận
    new_booking = Booking.query.get(booking_id)
    
    # 2. Kiểm tra xem thợ này đã có đơn nào trùng giờ chưa
    conflict = Booking.query.filter(
        Booking.provider_id == provider_id,
        Booking.status.in_(['accepted', 'in_progress']),
        Booking.scheduled_time == new_booking.scheduled_time
    ).first()
    
    if conflict:
        return jsonify({"message": "Bạn đã có lịch hẹn khác vào khung giờ này!"}), 400

    # 3. Nếu không trùng thì mới cho nhận
    new_booking.status = 'accepted'
    new_booking.provider_id = provider_id
    db.session.commit()
    return jsonify({"message": "Nhận đơn thành công!"}), 200

# --- 4. THỢ CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG (NHẬN ĐƠN / HOÀN THÀNH) ---
@app.route('/api/bookings/<int:booking_id>/status', methods=['PUT'])
def update_booking_status_by_worker(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Không tìm thấy đơn hàng"}), 404
        
    data = request.json
    new_status = data.get('status')
    
    # Cập nhật trạng thái (Ví dụ: pending -> accepted -> in_progress -> completed)
    if new_status in ['accepted', 'in_progress', 'completed', 'cancelled']:
        booking.status = new_status
        db.session.commit()
        return jsonify({"message": f"Đã chuyển trạng thái thành {new_status}!"}), 200
        
    return jsonify({"message": "Trạng thái không hợp lệ"}), 400

# --- CẬP NHẬT API GỬI ĐÁNH GIÁ ---
@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.json
    booking_id = data.get('booking_id')
    
    # 1. Tìm đơn hàng để lấy thông tin thợ và khách
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Không tìm thấy đơn hàng!"}), 404

    try:
        # 2. Tạo đánh giá mới, gán đầy đủ ID để tránh lỗi NOT NULL của MySQL
        new_review = Review(
            booking_id=booking_id,
            user_id=booking.user_id,
            provider_id=booking.provider_id, # Lấy ID thợ từ đơn hàng
            rating_star=data['stars'],
            comment=data.get('comment', '')
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": "Cảm ơn bạn đã đánh giá!"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi INSERT Review: {e}")
        return jsonify({"message": "Lỗi hệ thống khi lưu đánh giá"}), 500

@app.route('/api/provider/<int:provider_id>/notifications')
def get_notifications(provider_id):
    # Lấy các đơn hàng có lịch hẹn vào ngày mai
    tomorrow = datetime.now().date() + timedelta(days=1)
    upcoming_orders = Booking.query.filter(
        Booking.provider_id == provider_id,
        db.func.date(Booking.scheduled_time) == tomorrow
    ).all()
    
    return jsonify([{
        "title": "Nhắc hẹn ngày mai",
        "content": f"Bạn có đơn hàng {b.package_name} lúc {b.scheduled_time.strftime('%H:%M')}",
        "time": "Vừa xong"
    } for b in upcoming_orders])

# --- API: LẤY DANH SÁCH ĐÁNH GIÁ CỦA MỘT THỢ CỤ THỂ ---
@app.route('/api/provider/<int:provider_id>/reviews', methods=['GET'])
def get_provider_reviews(provider_id):
    # Kết nối 4 bảng: Review -> Booking -> User (Lấy tên khách) -> Service (Lấy tên dịch vụ)
    reviews = db.session.query(Review, Booking, User, Service)\
        .join(Booking, Review.booking_id == Booking.booking_id)\
        .join(User, Booking.user_id == User.user_id)\
        .join(Service, Booking.service_id == Service.service_id)\
        .filter(Booking.provider_id == provider_id)\
        .order_by(Review.review_id.desc()).all()

    result = []
    for r, b, u, s in reviews:
        result.append({
            "id": r.review_id,
            "customer_name": u.full_name,
            "service_name": f"{s.service_name} (Gói {b.package_name})",
            "stars": r.rating_star,
            "comment": r.comment
        })
    return jsonify(result), 200

# API lấy thông tin ví của thợ - ĐÃ CẬP NHẬT ĐỦ TRƯỜNG DỮ LIỆU
@app.route('/api/provider/<int:provider_id>/wallet')
def get_provider_wallet(provider_id):
    provider = Provider.query.get(provider_id)
    if not provider:
        return jsonify({"message": "Không tìm thấy thợ"}), 404
        
    # 1. Lấy TẤT CẢ lịch sử từ ví (Cả Nạp và Rút)
    # Loại bỏ các lệnh rút tiền bị Admin từ chối ('withdraw_rejected')
    wallet_txs = WalletTransaction.query.filter(
        WalletTransaction.provider_id == provider_id,
        WalletTransaction.transaction_type != 'withdraw_rejected'
    ).all()
    
    # Tính tổng tiền nạp/rút (Lưu ý: Lúc rút tiền mình đã lưu là số ÂM nên chỉ cần cộng lại hết là ra tổng)
    total_wallet_balance = sum(float(tx.amount) for tx in wallet_txs)
    
    # 2. Lấy đơn hàng hoàn thành để tính phí hệ thống
    completed_bookings = Booking.query.filter_by(provider_id=provider_id, status='completed').all()
    total_gross = sum(float(b.total_amount) for b in completed_bookings)
    total_fees = total_gross * 0.20
    
    # 3. TÍNH TOÁN SỐ DƯ THỰC TẾ: Tổng (Nạp - Rút) - Tổng phí
    actual_balance = total_wallet_balance - total_fees
    
    # Cập nhật ngược lại vào database để đồng bộ
    provider.balance = actual_balance
    db.session.commit()

    # 4. Tạo danh sách giao dịch hiển thị cho thợ
    display_transactions = []
    
    # Đổ các lệnh Nạp/Rút vào danh sách
    for tx in wallet_txs:
        amount_float = float(tx.amount)
        
        # Đặt màu sắc và tiêu đề tùy theo loại giao dịch
        if tx.transaction_type == 'deposit':
            title = "Nạp tiền vào ví"
            color = "#00c896" # Xanh lá
            amount_str = f"+{amount_float:,.0f}đ"
        elif tx.transaction_type == 'withdraw_pending':
            title = "Rút tiền (Đang chờ duyệt)"
            color = "#f59e0b" # Màu cam
            amount_str = f"{amount_float:,.0f}đ"
        elif tx.transaction_type == 'withdraw_completed':
            title = "Rút tiền (Thành công)"
            color = "#3b82f6" # Xanh dương
            amount_str = f"{amount_float:,.0f}đ"
            
        display_transactions.append({
            "type": title,
            "amount": amount_str,
            "date": tx.created_at.strftime('%d/%m/%Y %H:%M'),
            "description": tx.description,
            "color": color
        })
        
    # Đổ các lệnh trừ phí hệ thống vào danh sách
    for b in completed_bookings:
        fee = float(b.total_amount) * 0.20
        display_transactions.append({
            "type": "Trừ phí hệ thống (20%)",
            "amount": f"-{fee:,.0f}đ",
            "date": b.scheduled_time.strftime('%d/%m/%Y %H:%M'),
            "description": f"Đơn hàng #{b.booking_id}",
            "color": "#ef4444" # Màu đỏ
        })

    return jsonify({
        "balance": actual_balance,
        "total_gross": total_gross,
        "admin_fee": total_fees,
        "total_orders": len(completed_bookings),
        "transactions": display_transactions
    })

@app.route('/api/provider/<int:provider_id>/deposit', methods=['POST'])
def deposit_money(provider_id):
    data = request.json
    # 1. Ép kiểu số tiền nạp về float ngay từ đầu
    amount = float(data.get('amount', 0)) 
    
    provider = Provider.query.get(provider_id)
    if not provider:
        return jsonify({"message": "Không tìm thấy thợ"}), 404
        
    try:
        # 2. Xử lý trường hợp balance bị NULL trong database
        if provider.balance is None: 
            provider.balance = 0
        
        # 3. QUAN TRỌNG: Ép kiểu balance hiện tại sang float trước khi cộng
        # Điều này giúp tránh lỗi Decimal + float
        current_balance = float(provider.balance)
        provider.balance = current_balance + amount
        
        # 4. Ghi lại lịch sử nạp tiền vào bảng WalletTransactions
        new_tx = WalletTransaction(
            provider_id=provider_id,
            amount=amount,
            transaction_type='deposit',
            description=f"Nạp tiền vào ví tín dụng"
        )
        db.session.add(new_tx)
        
        db.session.commit()
        return jsonify({"message": f"Nạp thành công {amount:,.0f}đ vào ví!"}), 200
    except Exception as e:
        db.session.rollback()
        # In lỗi chi tiết ra terminal để bạn dễ theo dõi
        print(f"LỖI NẠP TIỀN: {str(e)}") 
        return jsonify({"message": str(e)}), 500

# ==========================================
# LUỒNG RÚT TIỀN (THỢ YÊU CẦU & ADMIN DUYỆT)
# ==========================================

# 1. API CHO THỢ: Gửi yêu cầu rút tiền
@app.route('/api/provider/<int:provider_id>/withdraw', methods=['POST'])
def request_withdraw(provider_id):
    data = request.json
    amount = float(data.get('amount', 0)) 
    
    # 1. LẤY SỐ TÀI KHOẢN TỪ FRONTEND GỬI LÊN
    bank_account = data.get('bank_account', 'Không rõ số TK')
    
    provider = Provider.query.get(provider_id)
    if not provider:
        return jsonify({"message": "Không tìm thấy thợ"}), 404
        
    try:
        current_balance = float(provider.balance or 0)
        
        if amount <= 0:
            return jsonify({"message": "Số tiền không hợp lệ"}), 400
        if current_balance < amount:
            return jsonify({"message": "Số dư trong ví không đủ để rút!"}), 400
            
        # Tạm giữ tiền (Trừ trên web)
        provider.balance = current_balance - amount
        
        # 2. LƯU KÈM SỐ TÀI KHOẢN VÀO PHẦN MÔ TẢ (DESCRIPTION)
        new_tx = WalletTransaction(
            provider_id=provider_id,
            amount=-amount, 
            transaction_type='withdraw_pending', 
            description=f"Yêu cầu rút tiền. STK: {bank_account}" # <-- Lưu số TK vào đây
        )
        db.session.add(new_tx)
        db.session.commit()
        
        return jsonify({"message": f"Đã gửi yêu cầu rút {amount:,.0f}đ về STK {bank_account}! Vui lòng chờ Admin duyệt."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

# 2. API CHO ADMIN: Lấy danh sách các lệnh đang chờ rút tiền
@app.route('/api/admin/withdrawals', methods=['GET'])
def admin_get_withdrawals():
    # Tìm các giao dịch có type là 'withdraw_pending'
    pending_txs = db.session.query(WalletTransaction, Provider)\
        .join(Provider, WalletTransaction.provider_id == Provider.provider_id)\
        .filter(WalletTransaction.transaction_type == 'withdraw_pending').all()
        
    result = []
    for tx, p in pending_txs:
        result.append({
            "tx_id": tx.id,
            "provider_name": p.full_name,
            "phone": p.phone_number,
            "amount": abs(float(tx.amount)), # Đổi số âm thành dương để dễ nhìn
            "date": tx.created_at.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(result), 200

# API CHO ADMIN: Lấy lịch sử rút tiền (đã duyệt hoặc từ chối)
@app.route('/api/admin/withdrawals/history', methods=['GET'])
def admin_get_withdrawal_history():
    history_txs = db.session.query(WalletTransaction, Provider)\
        .join(Provider, WalletTransaction.provider_id == Provider.provider_id)\
        .filter(WalletTransaction.transaction_type.in_(['withdraw_completed', 'withdraw_rejected']))\
        .order_by(WalletTransaction.id.desc()).all()
        
    result = []
    for tx, p in history_txs:
        result.append({
            "tx_id": tx.id,
            "provider_name": p.full_name,
            "phone": p.phone_number,
            "amount": abs(float(tx.amount)),
            "status": "Đã duyệt" if tx.transaction_type == 'withdraw_completed' else "Đã từ chối",
            "date": tx.created_at.strftime('%d/%m/%Y %H:%M')
        })
    return jsonify(result), 200

# 3. API CHO ADMIN: Duyệt hoặc Từ chối lệnh rút tiền
@app.route('/api/admin/withdrawals/<int:tx_id>', methods=['PUT'])
def admin_handle_withdrawal(tx_id):
    action = request.json.get('action') # 'approve' hoặc 'reject'
    tx = WalletTransaction.query.get(tx_id)
    
    if not tx or tx.transaction_type != 'withdraw_pending':
        return jsonify({"message": "Giao dịch không hợp lệ hoặc đã xử lý!"}), 400
        
    provider = Provider.query.get(tx.provider_id)
    
    try:
        if action == 'approve':
            tx.transaction_type = 'withdraw_completed'
            tx.description = "Rút tiền thành công (Đã duyệt)"
            db.session.commit()
            return jsonify({"message": "Đã duyệt lệnh rút tiền!"}), 200
            
        elif action == 'reject':
            tx.transaction_type = 'withdraw_rejected'
            tx.description = "Rút tiền bị từ chối (Đã hoàn tiền)"
            
            # HOÀN TIỀN LẠI VÀO VÍ CHO THỢ
            provider.balance = float(provider.balance or 0) + abs(float(tx.amount))
            db.session.commit()
            return jsonify({"message": "Đã từ chối và hoàn tiền lại cho thợ!"}), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi xử lý"}), 500

# ==========================================
# CÁC API CHO QUẢNG CÁO & ĐỀ XUẤT THỢ
# ==========================================
@app.route('/api/featured-providers', methods=['GET'])
def get_featured_providers():
    fps = FeaturedProvider.query.all()
    result = [{
        "id": fp.id,
        "badge": fp.badge,
        "avatar_icon": fp.avatar_icon,
        "provider_name": fp.provider_name,
        "description": fp.description,
        "rating": fp.rating,
        "review_count": fp.review_count,
        "tags": fp.tags,
        "price_text": fp.price_text,
        "service_link": fp.service_link
    } for fp in fps]
    return jsonify(result), 200

@app.route('/api/admin/featured-providers', methods=['POST'])
def add_featured_provider():
    data = request.json
    new_fp = FeaturedProvider(
        badge=data.get('badge'),
        avatar_icon=data.get('avatar_icon'),
        provider_name=data.get('provider_name'),
        description=data.get('description'),
        rating=float(data.get('rating', 5.0)),
        review_count=int(data.get('review_count', 0)),
        tags=data.get('tags'),
        price_text=data.get('price_text'),
        service_link=data.get('service_link')
    )
    db.session.add(new_fp)
    db.session.commit()
    return jsonify({"message": "Thêm đề xuất thành công!"}), 201

@app.route('/api/admin/featured-providers/<int:id>', methods=['PUT'])
def update_featured_provider(id):
    fp = FeaturedProvider.query.get(id)
    if not fp: return jsonify({"message": "Không tìm thấy"}), 404
    data = request.json
    fp.badge = data.get('badge', fp.badge)
    fp.avatar_icon = data.get('avatar_icon', fp.avatar_icon)
    fp.provider_name = data.get('provider_name', fp.provider_name)
    fp.description = data.get('description', fp.description)
    fp.rating = float(data.get('rating', fp.rating))
    fp.review_count = int(data.get('review_count', fp.review_count))
    fp.tags = data.get('tags', fp.tags)
    fp.price_text = data.get('price_text', fp.price_text)
    fp.service_link = data.get('service_link', fp.service_link)
    db.session.commit()
    return jsonify({"message": "Cập nhật thành công!"}), 200

@app.route('/api/admin/featured-providers/<int:id>', methods=['DELETE'])
def delete_featured_provider(id):
    fp = FeaturedProvider.query.get(id)
    if fp:
        db.session.delete(fp)
        db.session.commit()
    return jsonify({"message": "Đã xóa thành công!"}), 200

with app.app_context():
    db.create_all()
    # Tự động thêm các đề xuất cũ nếu Database trống
    if FeaturedProvider.query.count() == 0:
        default_fps = [
            FeaturedProvider(badge="🔥 Nổi bật", avatar_icon="👩‍🦱", provider_name="Nguyễn Thị Lan", description="Dọn dẹp nhà cửa · 5 năm KN", rating=5.0, review_count=128, tags="Dọn nhà, Giặt ủi, Lau kính", price_text="Từ 150.000 đ/buổi", service_link="/service/cleaning"),
            FeaturedProvider(badge="", avatar_icon="👨‍🔧", provider_name="Trần Văn Minh", description="Thợ điện nước · 8 năm KN", rating=5.0, review_count=95, tags="Sửa điện, Ống nước, Lắp đặt", price_text="Từ 120.000 đ/lần", service_link="/service/electric"),
            FeaturedProvider(badge="⭐ Quảng cáo", avatar_icon="🧑‍🔧", provider_name="Lê Quốc Hùng", description="Kỹ thuật viên máy lạnh · 6 năm KN", rating=4.0, review_count=74, tags="Vệ sinh ML, Bơm gas, Sửa chữa", price_text="Từ 200.000 đ/máy", service_link="/service/aircon"),
            FeaturedProvider(badge="", avatar_icon="👩‍💼", provider_name="Phạm Thị Hoa", description="Dọn dẹp & Vệ sinh · 4 năm KN", rating=5.0, review_count=61, tags="Dọn nhà, Lau kính", price_text="Từ 160.000 đ/buổi", service_link="/service/cleaning")
        ]
        db.session.add_all(default_fps)
        db.session.commit()

# ==========================================
# API CỘNG ĐỒNG - BÀI ĐĂNG (POSTS)
# ==========================================
import os as _os
from werkzeug.utils import secure_filename as _secure_filename

ALLOWED_MEDIA_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'mov', 'avi', 'webm'}

def allowed_media(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_MEDIA_EXTENSIONS

# --- LẤY TẤT CẢ BÀI ĐĂNG ---
@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    try:
        posts = Post.query.order_by(Post.created_at.desc()).all()
        result = []
        for p in posts:
            user = User.query.get(p.user_id)
            comments = PostComment.query.filter_by(post_id=p.post_id).order_by(PostComment.created_at.asc()).all()
            comment_list = []
            for c in comments:
                c_user = User.query.get(c.user_id)
                comment_list.append({
                    "comment_id": c.comment_id,
                    "user_id": c.user_id,
                    "content": c.content,
                    "created_at": c.created_at.strftime('%Y-%m-%d %H:%M:%S') if c.created_at else None,
                    "User": {"user_id": c_user.user_id, "full_name": c_user.full_name} if c_user else None
                })
            result.append({
                "post_id": p.post_id,
                "user_id": p.user_id,
                "content": p.content,
                "media_url": p.media_url,
                "media_type": p.media_type,
                "likes_count": p.likes_count or 0,
                "created_at": p.created_at.strftime('%Y-%m-%d %H:%M:%S') if p.created_at else None,
                "User": {"user_id": user.user_id, "full_name": user.full_name} if user else None,
                "PostComments": comment_list
            })
        return jsonify(result), 200
    except Exception as e:
        print("Lỗi lấy bài đăng:", e)
        return jsonify({"message": "Lỗi Server"}), 500

# --- ĐĂNG BÀI MỚI (hỗ trợ upload ảnh/video) ---
@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        user_id = request.form.get('user_id')
        content = request.form.get('content', '').strip()

        if not user_id:
            return jsonify({"message": "Thiếu thông tin người dùng!"}), 400
        if not content and 'media' not in request.files:
            return jsonify({"message": "Bài đăng phải có nội dung hoặc ảnh/video!"}), 400

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({"message": "Không tìm thấy người dùng"}), 404

        media_url = None
        media_type = None
        if 'media' in request.files:
            file = request.files['media']
            if file and file.filename != '' and allowed_media(file.filename):
                filename = _secure_filename(file.filename)
                safe_name = f"post_{int(datetime.utcnow().timestamp())}_{filename}"
                filepath = _os.path.join('static', 'uploads', safe_name)
                file.save(filepath)
                media_url = f"/static/uploads/{safe_name}"
                ext = filename.rsplit('.', 1)[1].lower()
                media_type = 'video' if ext in {'mp4', 'mov', 'avi', 'webm'} else 'image'

        new_post = Post(
            user_id=int(user_id),
            content=content if content else None,
            media_url=media_url,
            media_type=media_type,
            likes_count=0
        )
        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            "post_id": new_post.post_id,
            "user_id": new_post.user_id,
            "content": new_post.content,
            "media_url": new_post.media_url,
            "media_type": new_post.media_type,
            "likes_count": 0,
            "created_at": new_post.created_at.strftime('%Y-%m-%d %H:%M:%S') if new_post.created_at else None,
            "User": {"user_id": user.user_id, "full_name": user.full_name},
            "PostComments": []
        }), 201
    except Exception as e:
        db.session.rollback()
        print("Lỗi đăng bài:", e)
        return jsonify({"message": str(e) or "Lỗi Server"}), 500

# --- BÌNH LUẬN BÀI ĐĂNG ---
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    try:
        data = request.json
        user_id = data.get('user_id')
        content = (data.get('content') or '').strip()

        if not user_id or not content:
            return jsonify({"message": "Thiếu nội dung bình luận!"}), 400

        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Không tìm thấy bài đăng"}), 404

        comment = PostComment(
            post_id=post_id,
            user_id=int(user_id),
            content=content
        )
        db.session.add(comment)
        db.session.commit()

        user = User.query.get(int(user_id))
        return jsonify({
            "comment_id": comment.comment_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%Y-%m-%d %H:%M:%S') if comment.created_at else None,
            "User": {"user_id": user.user_id, "full_name": user.full_name} if user else None
        }), 201
    except Exception as e:
        db.session.rollback()
        print("Lỗi bình luận:", e)
        return jsonify({"message": "Lỗi Server"}), 500

# --- LIKE BÀI ĐĂNG ---
@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    try:
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Không tìm thấy bài đăng"}), 404
        post.likes_count = (post.likes_count or 0) + 1
        db.session.commit()
        return jsonify({"likes_count": post.likes_count}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi Server"}), 500

# --- XÓA BÀI ĐĂNG ---
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        data = request.json
        user_id = data.get('user_id')
        post = Post.query.get(post_id)
        if not post:
            return jsonify({"message": "Không tìm thấy bài đăng"}), 404
        if post.user_id != int(user_id):
            return jsonify({"message": "Bạn không có quyền xóa bài này!"}), 403
        PostComment.query.filter_by(post_id=post_id).delete()
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Đã xóa bài đăng thành công!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi Server"}), 500

# --- API LẤY HỒ SƠ CÔNG KHAI NGƯỜI DÙNG ---
@app.route('/api/user/<int:user_id>/public-profile', methods=['GET'])
def get_public_user_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Không tìm thấy người dùng"}), 404
        posts_count = Post.query.filter_by(user_id=user_id).count()
        return jsonify({
            "user_id": user.user_id,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url or "",
            "posts_count": posts_count
        }), 200
    except Exception as e:
        return jsonify({"message": "Lỗi Server"}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)