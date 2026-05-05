const express = require('express');
const router = express.Router();
const { User, Provider, Booking, Service } = require('../models');

// --- LẤY THÔNG TIN CÁ NHÂN ---
router.get('/:id', async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy" });

        const provider = await Provider.findOne({ where: { phone_number: user.phone_number } });
        let is_active_provider = false;
        let bio_text = "";

        if (provider && provider.status !== 'inactive') {
            is_active_provider = true;
            bio_text = provider.bio_description;
        }

        res.json({
            full_name: user.full_name,
            phone_number: user.phone_number,
            email: user.email,
            default_address: user.default_address || "",
            is_provider: is_active_provider,
            bio: bio_text,
            user_bio: user.bio || "",
            avatar_url: user.avatar_url || ""
        });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

// --- XEM ĐÁNH GIÁ CÔNG KHAI CỦA MỘT THỢ (tìm qua user_id) ---
const { Review } = require('../models');
router.get('/:id/public-reviews', async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy user" });

        const provider = await Provider.findOne({ where: { phone_number: user.phone_number } });
        if (!provider) return res.json([]); // Không phải thợ thì trả về mảng rỗng

        const reviews = await Review.findAll({
            where: { provider_id: provider.provider_id },
            include: [{ model: User, attributes: ['full_name'] }],
            order: [['created_at', 'DESC']],
            limit: 10
        });

        res.json(reviews.map(r => ({
            id: r.review_id,
            rating_star: r.rating_star,
            comment: r.comment,
            User: r.User
        })));
    } catch (err) {
        console.error("Lỗi lấy đánh giá:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

// --- CẬP NHẬT THÔNG TIN CÁ NHÂN & USER BIO ---
router.put('/:id/update-profile', async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy" });

        user.full_name = req.body.full_name || user.full_name;
        user.email = req.body.email || user.email;
        user.default_address = req.body.default_address || user.default_address;
        user.bio = req.body.user_bio || user.bio;
        await user.save();
        
        res.json({ message: "Cập nhật thông tin thành công!", user: { id: user.user_id, name: user.full_name, email: user.email, phone: user.phone_number, role: user.role } });
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

// --- THỢ CẬP NHẬT KINH NGHIỆM BIO ---
router.put('/:id/update-bio', async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        const provider = await Provider.findOne({ where: { phone_number: user.phone_number } });
        if (provider) {
            provider.bio_description = req.body.bio;
            await provider.save();
        }
        res.json({ message: "Đã cập nhật kinh nghiệm!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

// --- LẤY LỊCH SỬ ĐƠN HÀNG CỦA KHÁCH ---
router.get('/:id/bookings', async (req, res) => {
    try {
        const bookings = await Booking.findAll({
            where: { user_id: req.params.id },
            order: [['scheduled_time', 'DESC']],
            include: [Service, Provider]
        });

        res.json(bookings.map(b => ({
            id: b.booking_id,
            service_name: b.Service ? b.Service.service_name : 'Dịch vụ',
            package_name: b.package_name,
            time: b.scheduled_time ? b.scheduled_time.toLocaleString('vi-VN') : '',
            status: b.status,
            provider_name: b.Provider ? b.Provider.full_name : null,
            provider_id: b.provider_id,
            total_amount: b.total_amount
        })));
    } catch (err) { res.status(500).json({ message: 'Lỗi server!' }); }
});

const multer = require('multer');
const path = require('path');

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'static/uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, 'file_' + Date.now() + path.extname(file.originalname));
    }
});
const upload = multer({ storage: storage });

// --- ĐĂNG KÝ LÀM THỢ ---
router.post('/:id/register-provider', upload.single('evidence_image'), async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy User" });

        const existProvider = await Provider.findOne({ where: { phone_number: user.phone_number } });
        if (existProvider) {
            // Nếu tài khoản thợ đang active thì từ chối
            if (existProvider.status === 'active') {
                return res.status(400).json({ message: "Số điện thoại này đã được đăng ký và đang hoạt động!" });
            }
            // Nếu đang inactive (đã ngừng làm thợ, hoặc đang chờ duyệt), cho phép cập nhật lại thông tin
            existProvider.cccd_number = req.body.cccd;
            existProvider.bio_description = req.body.bio;
            if (req.file) {
                existProvider.evidence_url = '/static/uploads/' + req.file.filename;
            }
            existProvider.is_verified = false;
            existProvider.status = 'inactive';
            await existProvider.save();

            return res.json({ message: "Cập nhật hồ sơ thành công! Đang chờ duyệt lại." });
        }

        const newProvider = await Provider.create({
            full_name: user.full_name,
            phone_number: user.phone_number,
            cccd_number: req.body.cccd,
            bio_description: req.body.bio,
            evidence_url: req.file ? '/static/uploads/' + req.file.filename : null,
            avatar_url: user.avatar_url || null,
            is_verified: false,
            status: 'inactive'
        });

        res.json({ message: "Đăng ký thành công! Đang chờ duyệt." });
    } catch (err) {
        console.error("Lỗi đăng ký thợ:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

// --- NGỪNG LÀM THỢ ---
router.put('/:id/deactivate-provider', async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy User" });

        const provider = await Provider.findOne({ where: { phone_number: user.phone_number } });
        if (!provider) return res.status(404).json({ message: "Không tìm thấy thợ" });

        provider.status = 'inactive';
        await provider.save();

        res.json({ message: "Đã ngừng làm thợ thành công." });
    } catch (err) {
        console.error("Lỗi ngừng làm thợ:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

// --- CẬP NHẬT AVATAR CÁ NHÂN ---
router.post('/:id/avatar', upload.single('avatar'), async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy User" });

        if (!req.file) return res.status(400).json({ message: "Không có file ảnh" });

        const avatar_url = '/static/uploads/' + req.file.filename;
        user.avatar_url = avatar_url;
        await user.save();

        const provider = await Provider.findOne({ where: { phone_number: user.phone_number } });
        if (provider) {
            provider.avatar_url = avatar_url;
            await provider.save();
        }

        res.json({ message: "Cập nhật ảnh đại diện thành công!", avatar_url });
    } catch (err) {
        console.error("Lỗi cập nhật avatar:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

module.exports = router;
