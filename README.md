# 🏠 NTDVhome — Nền Tảng Kết Nối Dịch Vụ Tại Nhà

> **NTDVhome** là ứng dụng web kết nối người dùng với các chuyên gia/thợ dịch vụ tại nhà (dọn dẹp, sửa điện, sửa máy lạnh...). Hệ thống hỗ trợ 3 vai trò chính: Khách hàng, Thợ/Chuyên gia và Quản trị viên.

---

## 📑 Mục Lục

1. [Tính Năng](#-tính-năng)
2. [Công Nghệ & Kiến Trúc](#️-công-nghệ--kiến-trúc)
3. [Cơ Sở Dữ Liệu](#-cơ-sở-dữ-liệu)
4. [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
5. [Cài Đặt & Khởi Chạy](#️-cài-đặt--khởi-chạy)
6. [API Endpoints](#-api-endpoints)
7. [Phân Công Nhóm](#-phân-công-nhóm)

---

## ✨ Tính Năng

### 👤 Khách Hàng (Customer)
| Tính năng | Mô tả |
|---|---|
| Quản lý tài khoản | Đăng ký, đăng nhập, cập nhật thông tin cá nhân & avatar |
| Khôi phục mật khẩu | Nhận mã OTP qua email, xác thực và đặt lại mật khẩu |
| Tìm kiếm & đặt lịch | Xem dịch vụ, xem hồ sơ thợ, đặt lịch theo yêu cầu |
| Theo dõi đơn hàng | Xem trạng thái: Chờ xác nhận → Đang thực hiện → Hoàn thành / Đã hủy |
| Đánh giá thợ | Chấm điểm (rating) và để lại nhận xét sau khi hoàn thành |
| Nhắn tin trực tiếp | Inbox với thợ để trao đổi chi tiết công việc |
| Cộng đồng | Đăng bài, bình luận, tương tác trên bảng tin chung |

### 🔧 Thợ / Chuyên Gia (Provider)
| Tính năng | Mô tả |
|---|---|
| Đăng ký đối tác | Nộp hồ sơ kèm CCCD, chờ Admin phê duyệt |
| Quản lý đơn hàng | Nhận thông báo, chấp nhận/từ chối, cập nhật tiến độ |
| Ví tiền (Wallet) | Nạp tiền tín dụng, xem lịch sử giao dịch |
| Hoa hồng tự động | Hệ thống trừ 20% phí hoa hồng khi hoàn thành đơn |
| Rút tiền | Tạo yêu cầu rút doanh thu về tài khoản ngân hàng |
| Hồ sơ chuyên môn | Cập nhật bio, kinh nghiệm, loại dịch vụ cung cấp |
| Tương tác | Nhắn tin với khách, tham gia cộng đồng |

### 🛡️ Quản Trị Viên (Admin)
| Tính năng | Mô tả |
|---|---|
| Phê duyệt thợ | Kiểm tra CCCD, duyệt/từ chối hồ sơ đăng ký thợ mới |
| Quản lý người dùng | Xem danh sách, khóa/mở khóa tài khoản user & provider |
| Quản lý đơn hàng | Xem toàn bộ đơn đặt lịch và trạng thái trên hệ thống |
| Duyệt rút tiền | Xem xét và phê duyệt/từ chối yêu cầu rút tiền từ thợ |
| Thợ nổi bật | Cấu hình danh sách Featured Providers hiển thị trang chủ |
| Dashboard thống kê | Tổng số user, provider, đơn hàng, doanh thu, đánh giá |

---

## 🛠️ Công Nghệ & Kiến Trúc

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│          HTML5  •  CSS3  •  Vanilla JavaScript          │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP REST API
              ┌────────▼────────────┐
              │   Python — Flask    │
              │   Flask-SQLAlchemy  │
              │   Flask-CORS        │
              └────────┬────────────┘
                       │ SQLAlchemy ORM
              ┌────────▼────────┐
              │   MySQL Server  │
              │  ntdvhome_db    │
              │  (utf8mb4)      │
              └─────────────────┘
```

### Thư Viện & Công Cụ
| Mục đích | Thư viện |
|---|---|
| Framework | `Flask`, `Flask-CORS` |
| ORM | `Flask-SQLAlchemy` |
| DB Driver | `pymysql` |
| Mã hóa mật khẩu | `bcrypt` |
| Upload file | `werkzeug` |
| Gửi email OTP | `smtplib` (built-in Python) |
| Quản lý môi trường | `python-dotenv` |

---

## 🗄️ Cơ Sở Dữ Liệu

**Database:** `ntdvhome_db` — MySQL (charset: `utf8mb4`)

| Bảng | Mô tả |
|---|---|
| `Users` | Tài khoản khách hàng (tên, phone, email, mật khẩu, avatar, role) |
| `Providers` | Hồ sơ thợ (CCCD, ảnh bằng chứng, số dư ví, trạng thái duyệt) |
| `Services` | Danh mục dịch vụ (điện, nước, dọn dẹp, máy lạnh...) |
| `Bookings` | Đơn đặt lịch (liên kết User ↔ Provider ↔ Service, trạng thái đơn) |
| `Reviews` | Đánh giá & chấm sao sau khi hoàn thành đơn hàng |
| `DirectMessages` | Tin nhắn trực tiếp giữa người dùng với nhau |
| `ChatMessages` | Tin nhắn trao đổi theo đơn hàng (booking chat) |
| `WalletTransactions` | Lịch sử giao dịch ví thợ (nạp tiền, trừ hoa hồng, rút) |
| `Posts` | Bài đăng trên bảng tin cộng đồng |
| `PostComments` | Bình luận trên bài đăng cộng đồng |
| `FeaturedProviders` | Danh sách thợ nổi bật do Admin cấu hình hiển thị trang chủ |

> Chi tiết script SQL xem tại [`TaiLieu/DB.txt`](./TaiLieu/DB.txt)

---

## 📂 Cấu Trúc Thư Mục

```
NTDVhome/
│
├── templates/                  # Giao diện HTML (render bằng Jinja2)
│   ├── index.html              # Trang chủ
│   ├── login.html              # Đăng nhập
│   ├── register.html           # Đăng ký
│   ├── forgot-password.html    # Quên mật khẩu
│   ├── profile.html            # Hồ sơ cá nhân
│   ├── myorders.html           # Lịch sử đơn hàng (Customer)
│   ├── Booking.html            # Trang đặt lịch
│   ├── community.html          # Cộng đồng
│   ├── chat.html               # Nhắn tin trực tiếp
│   ├── provider-detail.html    # Hồ sơ chi tiết thợ
│   ├── user-profile.html       # Hồ sơ công khai người dùng
│   ├── service-detail.html     # Chi tiết dịch vụ
│   ├── Servicecleaning.html    # Dịch vụ dọn dẹp
│   ├── Serviceelectric.html    # Dịch vụ điện
│   ├── Serviceaircon.html      # Dịch vụ máy lạnh
│   ├── Workerorders.html       # Đơn hàng của thợ
│   ├── Workerincome.html       # Thu nhập & ví thợ
│   ├── Workerlocation.html     # Vị trí thợ
│   ├── Workernotifications.html# Thông báo thợ
│   ├── Workerreviews.html      # Đánh giá nhận được
│   ├── Workersettings.html     # Cài đặt tài khoản thợ
│   └── admin.html              # Dashboard quản trị
│
├── static/                     # File tĩnh
│   ├── style.css               # Stylesheet toàn cục
│   └── uploads/                # Ảnh upload (avatar, CCCD...)
│
├── TaiLieu/                    # Tài liệu dự án
│   ├── DB.txt                  # Script SQL tạo bảng thủ công
│   ├── NTDVHOME (1).docx       # Báo cáo đề tài
│   ├── poster3.png             # Poster dự án
│   └── ppt.pptx                # Slide thuyết trình
│
├── app.py                      # ⭐ Backend chính — Python/Flask
├── .env                        # Biến môi trường (không commit lên Git)
└── TaiLieu/DB.txt              # Script SQL tạo bảng
```

---

## ⚙️ Cài Đặt & Khởi Chạy

### Yêu Cầu
- **Python 3.x** (khuyên dùng 3.9 trở lên)
- **MySQL Server** đang chạy

### 1. Cấu Hình Database

Tạo database trong MySQL:
```sql
CREATE DATABASE ntdvhome_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Chạy script SQL khởi tạo bảng (tham chiếu tại [`TaiLieu/DB.txt`](./TaiLieu/DB.txt)).

### 2. Cấu Hình Biến Môi Trường

Tạo file `.env` tại thư mục gốc (hoặc chỉnh trực tiếp trong `app.py`):
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ntdvhome_db

SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
```

### 3. Cài Đặt Thư Viện

```bash
pip install flask flask-cors flask-sqlalchemy pymysql bcrypt python-dotenv
```

### 4. Khởi Chạy Server

```bash
python app.py
```

✅ Server khởi chạy tại: **`http://127.0.0.1:5000`**

> 💡 **Gợi ý:** Dùng `flask run --debug` để tự động reload khi chỉnh sửa code trong quá trình phát triển.

---

## 📡 API Endpoints

### 🔐 Authentication — `/api/auth`
| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/register` | Đăng ký tài khoản mới |
| `POST` | `/login` | Đăng nhập |
| `POST` | `/forgot-password` | Gửi mã OTP về email |
| `POST` | `/verify-otp` | Xác thực mã OTP |
| `POST` | `/reset-password` | Đặt lại mật khẩu mới |

### 👤 Người Dùng — `/api/user/:id`
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/user/:id` | Lấy thông tin hồ sơ cá nhân |
| `PUT` | `/api/user/:id` | Cập nhật thông tin cá nhân |
| `POST` | `/api/user/:id/avatar` | Cập nhật ảnh đại diện |
| `PUT` | `/api/user/:id/change-password` | Đổi mật khẩu |
| `PUT` | `/api/user/:id/update-bio` | Thợ cập nhật kinh nghiệm |
| `GET` | `/api/user/:id/bookings` | Xem lịch sử đặt lịch của user |

### 📅 Đặt Lịch & Đơn Hàng — `/api/bookings`
| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/api/bookings` | Tạo đơn đặt lịch mới |
| `GET` | `/api/bookings/:id` | Xem chi tiết một đơn hàng |
| `PUT` | `/api/bookings/:id/status` | Thợ cập nhật trạng thái đơn |
| `POST` | `/api/bookings/:id/review` | Khách hàng đánh giá thợ |

### 💬 Chat & Cộng Đồng
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/chat/:userId/conversations` | Danh sách cuộc trò chuyện |
| `GET` | `/api/chat/:userId/history/:otherId` | Lịch sử tin nhắn với một người |
| `POST` | `/api/chat/send` | Gửi tin nhắn mới |
| `GET` | `/api/posts` | Lấy danh sách bài viết cộng đồng |
| `POST` | `/api/posts` | Đăng bài viết mới |
| `POST` | `/api/posts/:id/comment` | Bình luận bài viết |

### 💰 Ví Tiền & Rút Tiền — `/api/provider/:id`
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/provider/:id/wallet` | Xem số dư & lịch sử giao dịch |
| `POST` | `/api/provider/:id/deposit` | Nạp tiền vào ví |
| `POST` | `/api/provider/:id/withdraw` | Tạo yêu cầu rút tiền |
| `GET` | `/api/provider/:id/orders` | Danh sách đơn hàng của thợ |

### 🌐 Public — `/api/public`
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/services` | Lấy danh sách dịch vụ |
| `GET` | `/api/public/providers/:id` | Xem hồ sơ công khai của thợ |
| `GET` | `/api/public/providers/:id/reviews` | Xem đánh giá của thợ |
| `GET` | `/api/featured-providers` | Lấy danh sách thợ nổi bật |

### 🛡️ Admin — `/api/admin`
| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/admin/users` | Danh sách toàn bộ user |
| `PUT` | `/api/admin/users/:id/role` | Thay đổi quyền user |
| `DELETE` | `/api/admin/users/:id` | Xóa tài khoản user |
| `GET` | `/api/admin/providers` | Danh sách toàn bộ thợ |
| `PUT` | `/api/admin/providers/:id/status` | Duyệt/khóa tài khoản thợ |
| `GET` | `/api/admin/bookings` | Xem tất cả đơn đặt lịch |
| `GET` | `/api/admin/withdrawals` | Danh sách yêu cầu rút tiền |
| `PUT` | `/api/admin/withdrawals/:id/status` | Duyệt/từ chối rút tiền |
| `GET` | `/api/admin/dashboard-stats` | Thống kê tổng quan |
| `GET/PUT/DELETE` | `/api/admin/featured-providers` | Quản lý thợ nổi bật |

---

## 👥 Phân Công Nhóm
Vương Quốc Cường	
Trưởng nhóm / Backend Developer:
• Thiết kế kiến trúc hệ thống và Cơ sở dữ liệu (MySQL).
• Xây dựng Backend bằng Python (Flask) và phát triển các RESTful API.
• Xử lý logic cốt lõi (Đặt lịch, thuật toán tìm thợ, phân quyền Admin).

Bùi Thị Như Thảo	
Frontend Developer / Tester:
• Thiết kế UI/UX và cắt giao diện bằng HTML5/CSS3/Vanilla JS
• Ghép nối API từ Backend lên giao diện người dùng.
• Xây dựng kịch bản kiểm thử (Test Cases) và thực hiện kiểm thử hộp đen.

Chen Woei Haur	
Business Analyst / Documentation:
• Phân tích yêu cầu nghiệp vụ và vẽ các sơ đồ hệ thống (Use Case, Activity Diagram).
• Hỗ trợ thiết kế Database và thu thập dữ liệu mẫu.
• Soạn thảo tài liệu báo cáo tổng kết đồ án và thiết kế Slide thuyết trình.


