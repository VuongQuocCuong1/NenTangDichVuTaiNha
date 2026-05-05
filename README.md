# NTDVhome Backend

Hệ thống Backend cho nền tảng **NTDVhome** - Ứng dụng kết nối người dùng với các chuyên gia/thợ sửa chữa, dọn dẹp tại nhà (Home Services Platform).

## 👥 Các Vai trò và Chức năng (Roles & Features)

Hệ thống NTDVhome được thiết kế với 3 vai trò chính, mỗi vai trò có các quyền và chức năng riêng biệt:

### 1. Khách hàng (Customer / User)
Người dùng tìm kiếm và đặt lịch các dịch vụ tại nhà.
*   **Quản lý Tài khoản:** Đăng ký, đăng nhập, quên mật khẩu (nhận mã OTP qua email), cập nhật thông tin cá nhân (avatar, họ tên, số điện thoại, địa chỉ).
*   **Tìm kiếm & Đặt lịch:** Xem danh sách dịch vụ, xem hồ sơ của thợ, đặt lịch dịch vụ theo yêu cầu.
*   **Quản lý Đơn hàng:** Xem lịch sử đặt lịch, theo dõi trạng thái đơn hàng (Chờ xác nhận, Đang thực hiện, Hoàn thành, Đã hủy).
*   **Tương tác & Giao tiếp:**
    *   Nhắn tin trực tiếp (Inbox) với thợ để trao đổi chi tiết công việc.
    *   Tham gia cộng đồng: Đăng bài, bình luận, tương tác trên bảng tin chung.
*   **Đánh giá & Phản hồi:** Đánh giá, chấm điểm (rating) cho thợ sau khi hoàn thành công việc.

### 2. Thợ / Chuyên gia (Provider)
Người cung cấp các dịch vụ tiện ích tại nhà (dọn dẹp, sửa chữa điện nước, máy lạnh...).
*   **Đăng ký Đối tác:** Đăng ký tài khoản thợ, tải lên giấy tờ tùy thân (CCCD) và chờ Admin phê duyệt.
*   **Quản lý Hồ sơ & Dịch vụ:** Cập nhật thông tin chuyên môn, kinh nghiệm, chọn loại dịch vụ cung cấp.
*   **Quản lý Đơn hàng:** Nhận thông báo đơn hàng mới, chấp nhận/từ chối đơn hàng, cập nhật tiến độ công việc (Đã nhận, Đang làm, Hoàn thành).
*   **Quản lý Ví (Wallet) & Doanh thu:**
    *   Nạp tiền vào ví tín dụng.
    *   Hệ thống tự động trừ phí hoa hồng (20%) khi hoàn thành một đơn đặt hàng.
    *   Xem lịch sử giao dịch (nạp tiền, trừ phí, rút tiền).
    *   Tạo yêu cầu rút tiền doanh thu về tài khoản ngân hàng.
*   **Tương tác:** Nhắn tin trực tiếp với khách hàng từ các đơn đặt lịch, tham gia cộng đồng tương tự User.

### 3. Quản trị viên (Admin)
Người quản lý và điều hành toàn bộ hệ thống nền tảng.
*   **Quản lý Người dùng & Thợ:** Xem danh sách, khóa/mở khóa tài khoản khách hàng và thợ.
*   **Phê duyệt Tài khoản:** Duyệt hồ sơ đăng ký của thợ mới (kiểm tra CCCD, thông tin).
*   **Quản lý Đơn hàng:** Xem tất cả các đơn đặt lịch trên hệ thống và trạng thái.
*   **Quản lý Rút tiền:** Xem xét và phê duyệt/từ chối các yêu cầu rút tiền từ thợ.
*   **Quản lý Thợ nổi bật:** Cấu hình danh sách thợ nổi bật (Featured Providers) hiển thị ở trang chủ.
*   **Thống kê:** Xem dashboard thống kê tổng quan (tổng số user, provider, số đơn hàng, doanh thu).

## 🛠 Công nghệ & Kiến trúc (Tech Stack)

Dự án hiện tại đang được vận hành bằng kiến trúc MVC trên nền tảng **Node.js (Express.js)**. Đồng thời, phiên bản cũ viết bằng **Python (Flask)** vẫn được giữ lại để dự phòng.

*   **Node.js (Phiên bản chính)**
    *   Framework: `Express.js`
    *   ORM: `Sequelize`
*   **Python (Phiên bản cũ)**
    *   Framework: `Flask`, `Flask-CORS`
    *   ORM: `Flask-SQLAlchemy`
*   **Cơ sở dữ liệu:** MySQL (`ntdvhome_db` - charset `utf8mb4`)
*   **Các thư viện hỗ trợ:**
    *   `bcryptjs` / `bcrypt`: Mã hóa mật khẩu.
    *   `multer`: Xử lý upload file (ảnh đại diện, CCCD).
    *   `nodemailer`: Gửi email mã OTP khôi phục mật khẩu.

## 📂 Cấu trúc thư mục (Folder Structure)

NTDVhome/
│
├── config/              # Chứa cấu hình kết nối Database (Node.js)
├── models/              # Định nghĩa các model Sequelize (User, Provider, Booking, Service, ...)
├── routes/              # Chứa các Controller API xử lý logic (auth, bookings, chat, admin, ...)
├── static/              # Thư mục chứa file tĩnh lưu trữ hệ thống (Hình ảnh upload: avatars, cccd, css, js)
├── templates/           # Chứa các giao diện HTML (Frontend test hoặc giao diện render bằng Jinja2)
│
├── app.py               # File chạy Backend phiên bản Python Flask (Legacy)
├── server.js            # File chạy Backend phiên bản Node.js Express (Main)
├── alter_chat_db.js     # Script tạo/cập nhật bảng cơ sở dữ liệu
├── package.json         # Khai báo thư viện và thông tin dự án Node.js
└── DB.txt               # Ghi chú hoặc script SQL tạo bảng database thủ công
```

## ⚙️ Hướng dẫn Cài đặt & Khởi chạy (Setup & Run)

### Yêu cầu trước khi chạy
*   Đã cài đặt **Node.js** (Khuyên dùng v16 trở lên) và **MySQL Server**.
*   Tạo database trong MySQL với tên là `ntdvhome_db`.
*   Cấu hình thông tin đăng nhập MySQL trong `config/database.js` và `app.py` (Mặc định: username `root`, password `123456`).

### Khởi chạy bằng Node.js (Khuyên dùng - Express MVC)
1. Mở terminal tại thư mục `Backend/`.
2. Cài đặt các thư viện phụ thuộc:
   ```bash
   npm install
   ```
3. Khởi chạy server ở chế độ Development (tự động reload khi có thay đổi code):
   ```bash
   npm run dev
   ```
   *(Hoặc chạy bình thường: `npm start`)*
4. Server chạy thành công tại địa chỉ: `http://127.0.0.1:5000`

### Khởi chạy bằng Python (Legacy - Flask)
1. Cài đặt Python 3.x.
2. Mở terminal tại thư mục `Backend/` và cài đặt các thư viện:
   ```bash
   pip install flask flask-cors flask-sqlalchemy pymysql bcrypt
   ```
3. Khởi chạy server:
   ```bash
   python app.py
   ```
4. Server chạy thành công tại địa chỉ: `http://127.0.0.1:5000`

> ⚠️ **Lưu ý:** Cả bản Node.js và Python đều cấu hình mặc định chạy trên cổng (port) `5000`. Hãy đảm bảo chỉ chạy 1 phiên bản tại 1 thời điểm.

## 📡 Các API Endpoints chính (Main API Routes)

**1. Authentication (`/api/auth`)**
*   `POST /register`: Đăng ký tài khoản (User/Provider).
*   `POST /login`: Đăng nhập.
*   `POST /forgot-password`, `POST /verify-otp`, `POST /reset-password`: Quy trình lấy lại mật khẩu.

**2. Đặt lịch & Đơn hàng (`/api/bookings`, `/api/provider/:id/orders`)**
*   `POST /`: Tạo đơn đặt lịch mới (User).
*   `GET /user/:id`: Lấy danh sách lịch đã đặt của User.
*   `GET /provider/:id/orders`: Lấy danh sách đơn hàng được giao cho Provider.
*   `PUT /:id/status`: Provider cập nhật trạng thái đơn hàng.

**3. Giao tiếp & Cộng đồng (`/api/chat`, `/api/posts`)**
*   `GET /:userId/conversations`: Lấy danh sách cuộc trò chuyện.
*   `GET /:userId/messages/:otherId`: Lấy tin nhắn chi tiết.
*   `POST /send`: Gửi tin nhắn mới.
*   `GET /posts`, `POST /posts`: Xem và đăng bài viết cộng đồng.

**4. Ví tiền & Rút tiền (`/api/provider/:id/wallet`, `/api/provider/:id/withdraw`)**
*   `GET /`: Xem số dư và lịch sử giao dịch.
*   `POST /deposit`: Nạp tiền vào ví.
*   `POST /withdraw`: Tạo yêu cầu rút tiền.

**5. Quản trị viên (`/api/admin`)**
*   `GET /users`, `GET /providers`: Quản lý tài khoản.
*   `GET /bookings`: Xem tất cả đơn hàng.
*   `GET /withdrawals`, `PUT /withdrawals/:id/status`: Duyệt yêu cầu rút tiền.
*   `PUT /providers/:id/status`: Phê duyệt tài khoản thợ mới.
