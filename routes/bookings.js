const express = require('express');
const router = express.Router();
const { Booking, User, Service, ChatMessage, Review } = require('../models');
const { Op } = require('sequelize');

// --- TẠO ĐƠN HÀNG MỚI (TỪ KHÁCH) ---
router.post('/', async (req, res) => {
    try {
        const {
            user_id, provider_id, service_id,
            package_name,
            price, total_price,           // Chấp nhận cả 2 tên field
            address,
            time, date                    // Frontend có thể gửi date+time riêng, hoặc time đầy đủ
        } = req.body;

        // Xây dựng scheduled_time
        let scheduledTime;
        if (date && time) {
            // Chế độ "Đặt lịch trước": frontend gửi date='2025-05-10' và time='09:00'
            scheduledTime = new Date(`${date}T${time}:00`);
        } else if (time && time.trim() !== '') {
            scheduledTime = new Date(time);
        } else {
            // Chế độ "Đặt ngay": dùng thời gian hiện tại
            scheduledTime = new Date();
        }

        // Kiểm tra ngày hợp lệ
        if (isNaN(scheduledTime.getTime())) {
            return res.status(400).json({ message: 'Thời gian không hợp lệ! Vui lòng chọn lại ngày giờ.' });
        }

        const finalAmount = price || total_price || 0;
        const finalAddress = address || '';

        if (!finalAddress.trim()) {
            return res.status(400).json({ message: 'Vui lòng nhập địa chỉ dịch vụ!' });
        }

        const newBooking = await Booking.create({
            user_id:        user_id,
            provider_id:    provider_id || null,
            service_id:     service_id || 1,
            package_name:   package_name || '',
            total_amount:   finalAmount,
            service_address: finalAddress,
            scheduled_time: scheduledTime,
            status: 'pending'
        });

        res.status(201).json({
            message: 'Đặt lịch thành công!',
            booking_id: newBooking.booking_id
        });
    } catch (err) {
        console.error('❌ Lỗi tạo đơn hàng:', err);
        res.status(500).json({ message: 'Lỗi server!', detail: err.message });
    }
});

// --- LẤY 1 ĐƠN HÀNG ---
router.get('/:id', async (req, res) => {
    try {
        const { Provider } = require('../models');
        const b = await Booking.findByPk(req.params.id, {
            include: [User, Service, Provider]
        });
        if (!b) return res.status(404).json({ message: 'Không tìm thấy' });

        let providerData = null;
        if (b.Provider) {
            providerData = {
                name:   b.Provider.full_name,
                phone:  b.Provider.phone_number,
                bio:    b.Provider.bio_description || 'Chuyên gia',
                avatar: b.Provider.avatar_url || null
            };
        }

        res.json({
            id:           b.booking_id,
            customer_name:  b.User ? b.User.full_name : 'Khách',
            customer_phone: b.User ? b.User.phone_number : '',
            service_name:   b.Service ? b.Service.service_name : 'Dịch vụ',
            package_name:   b.package_name || '',
            address:        b.service_address || '',
            total_price:    b.total_amount || 0,
            time:           b.scheduled_time
                              ? b.scheduled_time.toLocaleString('vi-VN')
                              : 'Chưa xác định',
            status:         b.status,
            provider:       providerData
        });
    } catch (err) {
        console.error('❌ Lỗi GET booking:', err);
        res.status(500).json({ message: 'Lỗi server', detail: err.message });
    }
});


// --- THỢ NHẬN ĐƠN ---
router.put('/:id/accept', async (req, res) => {
    try {
        const { provider_id } = req.body;
        const booking = await Booking.findByPk(req.params.id);
        if(!booking) return res.status(404).json({ message: "Không tìm thấy đơn" });
        
        // Cần kiểm tra trùng lịch (Bỏ qua logic phức tạp để code chạy trơn tru)
        booking.status = 'accepted';
        booking.provider_id = provider_id;
        await booking.save();
        res.json({ message: "Nhận đơn thành công!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

// --- THỢ CẬP NHẬT TRẠNG THÁI ---
router.put('/:id/status', async (req, res) => {
    try {
        const booking = await Booking.findByPk(req.params.id);
        if(!booking) return res.status(404).json({ message: "Không tìm thấy" });
        booking.status = req.body.status;
        await booking.save();
        res.json({ message: `Chuyển trạng thái thành ${booking.status}` });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

// --- CHAT TIN NHẮN TRONG ĐƠN HÀNG ---
router.get('/:id/chat', async (req, res) => {
    try {
        const messages = await ChatMessage.findAll({
            where: { booking_id: req.params.id },
            order: [['id', 'ASC']]
        });
        res.json(messages.map(m => ({
            id: m.id,
            sender_type: m.sender_type,
            message: m.message,
            time: m.created_at
                ? new Date(m.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
                : new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
        })));
    } catch (err) {
        console.error('❌ Lỗi GET chat:', err);
        res.status(500).json({ message: 'Lỗi server', detail: err.message });
    }
});

router.post('/:id/chat', async (req, res) => {
    try {
        const { sender_type, message } = req.body;
        if (!message || !message.trim()) {
            return res.status(400).json({ message: 'Tin nhắn không được để trống!' });
        }
        await ChatMessage.create({
            booking_id: parseInt(req.params.id),
            sender_type: sender_type || 'customer',
            message: message.trim(),
            created_at: new Date()
        });
        res.status(201).json({ message: 'Đã gửi' });
    } catch (err) {
        console.error('❌ Lỗi POST chat:', err);
        res.status(500).json({ message: 'Lỗi server', detail: err.message });
    }
});

// --- KHÁCH ĐÁNH GIÁ SAU KHI HOÀN THÀNH ---
router.post('/review', async (req, res) => {
    try {
        const { booking_id, provider_id, user_id, rating_star, comment } = req.body;
        if (!provider_id || !user_id || !rating_star) {
            return res.status(400).json({ message: 'Thiếu thông tin đánh giá!' });
        }
        // Kiểm tra đã đánh giá chưa
        const existing = await Review.findOne({ where: { booking_id } });
        if (existing) return res.status(400).json({ message: 'Bạn đã đánh giá đơn hàng này rồi!' });

        await Review.create({
            booking_id,
            provider_id,
            user_id,
            rating_star: Math.min(5, Math.max(1, parseInt(rating_star))),
            comment: comment || ''
        });
        res.json({ message: 'Đánh giá thành công! Cảm ơn bạn.' });
    } catch (err) {
        console.error('❌ Lỗi tạo đánh giá:', err);
        res.status(500).json({ message: 'Lỗi server!', detail: err.message });
    }
});

module.exports = router;

