const express = require('express');
const router = express.Router();
const { User, Provider, Service, Booking, Review, FeaturedProvider, WalletTransaction } = require('../models');
const { Op } = require('sequelize');

router.get('/dashboard-stats', async (req, res) => {
    try {
        const total_providers = await Provider.count({ where: { is_verified: true } });
        const completed_bookings = await Booking.findAll({ where: { status: 'completed' } });
        let total_revenue = 0;
        completed_bookings.forEach(b => { if (b.total_amount) total_revenue += parseFloat(b.total_amount) * 0.20; });
        const five_star_reviews = await Review.count({ where: { rating_star: 5 } });
        const bad_reviews = await Review.count({ where: { rating_star: { [Op.lte]: 2 } } });
        res.json({ total_providers, total_revenue, five_star_reviews, bad_reviews });
    } catch (err) { res.status(500).json({ message: "Lỗi Dashboard" }); }
});

router.get('/users', async (req, res) => {
    try {
        const users = await User.findAll();
        res.json(users.map(u => ({ user_id: u.user_id, full_name: u.full_name, phone_number: u.phone_number, email: u.email, role: u.role })));
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.put('/users/:id/role', async (req, res) => {
    try {
        const user = await User.findByPk(req.params.id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy" });
        user.role = req.body.role || 'user';
        await user.save();
        res.json({ message: "Cập nhật quyền thành công!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.delete('/users/:id', async (req, res) => {
    try {
        await User.destroy({ where: { user_id: req.params.id } });
        res.json({ message: "Đã xóa người dùng thành công!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.get('/providers', async (req, res) => {
    try {
        const providers = await Provider.findAll();
        res.json(providers.map(p => ({ id: p.provider_id, name: p.full_name, phone: p.phone_number, cccd: p.cccd_number, bio: p.bio_description, avatar: p.avatar_url, verified: p.is_verified, status: p.status })));
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.put('/providers/:id/status', async (req, res) => {
    try {
        const p = await Provider.findByPk(req.params.id);
        if ('status' in req.body) p.status = req.body.status;
        if ('verified' in req.body) p.is_verified = req.body.verified;
        await p.save();
        res.json({ message: "Đã cập nhật thợ!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.get('/reviews', async (req, res) => {
    try {
        const reviews = await Review.findAll({ include: [User, Provider] });
        res.json(reviews.map(r => ({ 
            id: r.review_id, 
            customer: r.User ? r.User.full_name : 'Khách', 
            provider: r.Provider ? r.Provider.full_name : 'Không xác định',
            stars: r.rating_star, 
            comment: r.comment 
        })));
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.delete('/reviews/:id', async (req, res) => {
    try {
        await Review.destroy({ where: { review_id: req.params.id } });
        res.json({ message: "Đã xóa đánh giá!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.get('/bookings', async (req, res) => {
    try {
        const bookings = await Booking.findAll({
            include: [
                { model: User, required: false },
                { model: Service, required: false },
                { model: Provider, required: false }
            ],
            order: [['booking_id', 'DESC']]
        });
        res.json(bookings.map(b => ({
            id: b.booking_id,
            customer: b.User ? b.User.full_name : 'Khách',
            service: b.Service ? b.Service.service_name : 'Dịch vụ',
            address: b.service_address || 'Không rõ',
            time: b.scheduled_time ? new Date(b.scheduled_time).toLocaleString('vi-VN') : 'Không rõ',
            status: b.status || 'pending',
            provider: b.Provider ? b.Provider.full_name : 'Chưa phân công',
            amount: b.total_amount ? parseFloat(b.total_amount).toLocaleString('vi-VN') + ' đ' : 'N/A'
        })));
    } catch (err) {
        console.error('❌ Lỗi GET /admin/bookings:', err);
        res.status(500).json({ message: 'Lỗi server!', detail: err.message });
    }
});

router.get('/withdrawals', async (req, res) => {
    try {
        const pending_txs = await WalletTransaction.findAll({
            where: { transaction_type: 'withdraw_pending' },
            include: [{ model: Provider, attributes: ['full_name', 'phone_number'] }]
        });
        
        const result = pending_txs.map(tx => ({
            tx_id: tx.id,
            provider_name: tx.Provider ? tx.Provider.full_name : 'Unknown',
            phone: tx.Provider ? tx.Provider.phone_number : 'Unknown',
            amount: Math.abs(parseFloat(tx.amount)),
            date: tx.created_at ? tx.created_at.toLocaleString('vi-VN') : ''
        }));
        res.json(result);
    } catch (err) {
        console.error("Lỗi lấy danh sách rút tiền chờ duyệt:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

router.get('/withdrawals/history', async (req, res) => {
    try {
        const history_txs = await WalletTransaction.findAll({
            where: { 
                transaction_type: { [Op.in]: ['withdraw_completed', 'withdraw_rejected'] } 
            },
            include: [{ model: Provider, attributes: ['full_name', 'phone_number'] }],
            order: [['id', 'DESC']]
        });
        
        const result = history_txs.map(tx => ({
            tx_id: tx.id,
            provider_name: tx.Provider ? tx.Provider.full_name : 'Unknown',
            phone: tx.Provider ? tx.Provider.phone_number : 'Unknown',
            amount: Math.abs(parseFloat(tx.amount)),
            status: tx.transaction_type === 'withdraw_completed' ? 'Đã duyệt' : 'Đã từ chối',
            date: tx.created_at ? tx.created_at.toLocaleString('vi-VN') : ''
        }));
        res.json(result);
    } catch (err) {
        console.error("Lỗi lấy lịch sử rút tiền:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

router.put('/withdrawals/:id', async (req, res) => {
    try {
        const action = req.body.action; // 'approve' hoặc 'reject'
        const tx = await WalletTransaction.findByPk(req.params.id);
        
        if (!tx || tx.transaction_type !== 'withdraw_pending') {
            return res.status(400).json({ message: "Giao dịch không hợp lệ hoặc đã xử lý!" });
        }
        
        const provider = await Provider.findByPk(tx.provider_id);
        if (!provider) {
            return res.status(404).json({ message: "Không tìm thấy thợ liên quan!" });
        }

        if (action === 'approve') {
            tx.transaction_type = 'withdraw_completed';
            tx.description = "Rút tiền thành công (Đã duyệt)";
            await tx.save();
            return res.json({ message: "Đã duyệt lệnh rút tiền!" });
        } else if (action === 'reject') {
            tx.transaction_type = 'withdraw_rejected';
            tx.description = "Rút tiền bị từ chối (Đã hoàn tiền)";
            await tx.save();
            
            // Hoàn tiền lại ví cho thợ
            provider.balance = parseFloat(provider.balance || 0) + Math.abs(parseFloat(tx.amount));
            await provider.save();
            
            return res.json({ message: "Đã từ chối và hoàn tiền lại cho thợ!" });
        } else {
            return res.status(400).json({ message: "Hành động không hợp lệ!" });
        }
    } catch (err) {
        console.error("Lỗi xử lý duyệt rút tiền:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

module.exports = router;
