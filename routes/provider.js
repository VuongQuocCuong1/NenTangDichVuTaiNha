const express = require('express');
const router = express.Router();
const { Booking, User, Service, Review, Provider, WalletTransaction } = require('../models');
const { Op } = require('sequelize');

// --- LẤY DANH SÁCH ĐƠN HÀNG CHO THỢ ---
router.get('/:id/orders', async (req, res) => {
    try {
        const bookings = await Booking.findAll({
            where: { provider_id: req.params.id },
            order: [['scheduled_time', 'ASC']],
            include: [User, Service]
        });

        res.json(bookings.map(b => ({
            id: b.booking_id,
            customer_name: b.User ? b.User.full_name : 'Khách',
            customer_phone: b.User ? b.User.phone_number : 'Không có',
            service_name: b.Service ? b.Service.service_name : 'Dịch vụ',
            package_name: b.package_name,
            address: b.service_address,
            time: b.scheduled_time ? b.scheduled_time.toLocaleString('vi-VN') : 'Không rõ',
            status: b.status,
            price: b.total_amount
        })));
    } catch (err) {
        console.error("Lỗi lấy đơn hàng thợ:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// --- LẤY ĐÁNH GIÁ CHO THỢ ---
router.get('/:id/reviews', async (req, res) => {
    try {
        const reviews = await Review.findAll({
            where: { provider_id: req.params.id },
            include: [
                { model: User, attributes: ['full_name'] },
                { model: Booking, include: [{ model: Service, attributes: ['service_name'] }] }
            ],
            order: [['created_at', 'DESC']]
        });

        res.json(reviews.map(r => ({
            id: r.review_id,
            customer_name: r.User ? r.User.full_name : 'Khách',
            service_name: (r.Booking && r.Booking.Service) ? r.Booking.Service.service_name : 'Dịch vụ',
            stars: r.rating_star,
            comment: r.comment,
            date: r.created_at
        })));
    } catch (err) {
        console.error("Lỗi lấy đánh giá thợ:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// --- LẤY THÔNG TIN VÍ & THU NHẬP ---
router.get('/:id/wallet', async (req, res) => {
    try {
        const provider = await Provider.findByPk(req.params.id);
        if (!provider) return res.status(404).json({ message: "Không tìm thấy thợ" });

        const completedBookings = await Booking.findAll({ where: { provider_id: req.params.id, status: 'completed' } });
        const totalOrders = completedBookings.length;
        let totalGross = 0;
        completedBookings.forEach(b => {
            if (b.total_amount) totalGross += parseFloat(b.total_amount);
        });
        const adminFee = totalGross * 0.20;

        const transactions = await WalletTransaction.findAll({
            where: { provider_id: req.params.id },
            order: [['created_at', 'DESC']]
        });

        res.json({
            balance: provider.balance,
            total_gross: totalGross,
            admin_fee: adminFee,
            total_orders: totalOrders,
            transactions: transactions.map(t => {
                let isAdd = t.transaction_type === 'deposit' || t.transaction_type === 'income';
                let sign = isAdd ? '+' : '-';
                let color = isAdd ? '#10b981' : '#ef4444';
                let typeName = t.transaction_type === 'deposit' ? 'Nạp tiền vào ví' :
                               t.transaction_type === 'withdraw' ? 'Rút tiền' :
                               t.transaction_type === 'income' ? 'Cộng thu nhập' : 'Trừ phí / Khác';

                return {
                    type: typeName,
                    date: t.created_at ? t.created_at.toLocaleString('vi-VN') : '',
                    description: t.description,
                    amount: `${sign}${parseFloat(t.amount).toLocaleString('vi-VN')} đ`,
                    color: color
                };
            })
        });
    } catch (err) {
        console.error("Lỗi lấy ví:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// --- NẠP TIỀN VÀO VÍ ---
router.post('/:id/deposit', async (req, res) => {
    try {
        const amount = parseFloat(req.body.amount);
        if (isNaN(amount) || amount <= 0) return res.status(400).json({ message: "Số tiền không hợp lệ" });

        const provider = await Provider.findByPk(req.params.id);
        if (!provider) return res.status(404).json({ message: "Không tìm thấy thợ" });

        provider.balance = parseFloat(provider.balance) + amount;
        await provider.save();

        await WalletTransaction.create({
            provider_id: req.params.id,
            amount: amount,
            transaction_type: 'deposit',
            description: 'Nạp tiền vào ví tín dụng'
        });

        res.json({ message: `Đã nạp thành công ${amount.toLocaleString('vi-VN')} đ` });
    } catch (err) {
        console.error("Lỗi nạp tiền:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// --- RÚT TIỀN TỪ VÍ ---
router.post('/:id/withdraw', async (req, res) => {
    try {
        const amount = parseFloat(req.body.amount);
        const bankAccount = req.body.bank_account;
        if (isNaN(amount) || amount <= 0) return res.status(400).json({ message: "Số tiền không hợp lệ" });
        if (!bankAccount) return res.status(400).json({ message: "Thiếu số tài khoản" });

        const provider = await Provider.findByPk(req.params.id);
        if (!provider) return res.status(404).json({ message: "Không tìm thấy thợ" });

        if (parseFloat(provider.balance) < amount) {
            return res.status(400).json({ message: "Số dư ví không đủ để rút" });
        }

        provider.balance = parseFloat(provider.balance) - amount;
        await provider.save();

        await WalletTransaction.create({
            provider_id: req.params.id,
            amount: amount,
            transaction_type: 'withdraw',
            description: `Rút tiền về tài khoản: ${bankAccount}`
        });

        res.json({ message: `Đã rút ${amount.toLocaleString('vi-VN')} đ thành công` });
    } catch (err) {
        console.error("Lỗi rút tiền:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

module.exports = router;
