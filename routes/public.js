const express = require('express');
const router = express.Router();
const path = require('path');
const { Service, FeaturedProvider, Provider, Review } = require('../models');

// === HTML PAGES ===
const viewPath = path.join(__dirname, '../templates');
router.get('/', (req, res) => res.sendFile(path.join(viewPath, 'index.html')));
router.get('/login', (req, res) => res.sendFile(path.join(viewPath, 'login.html')));
router.get('/register', (req, res) => res.sendFile(path.join(viewPath, 'register.html')));
router.get('/forgot-password', (req, res) => res.sendFile(path.join(viewPath, 'forgot-password.html')));
router.get('/profile', (req, res) => res.sendFile(path.join(viewPath, 'profile.html')));
router.get('/provider-detail', (req, res) => res.sendFile(path.join(viewPath, 'provider-detail.html')));
router.get('/booking', (req, res) => res.sendFile(path.join(viewPath, 'Booking.html')));
router.get('/admin', (req, res) => res.sendFile(path.join(viewPath, 'admin.html')));
router.get('/community', (req, res) => res.sendFile(path.join(viewPath, 'community.html')));
router.get('/chat', (req, res) => res.sendFile(path.join(viewPath, 'chat.html')));
router.get('/user-profile/:userId', (req, res) => res.sendFile(path.join(viewPath, 'user-profile.html')));
router.get('/my-orders', (req, res) => res.sendFile(path.join(viewPath, 'myorders.html')));
router.get('/worker/orders', (req, res) => res.sendFile(path.join(viewPath, 'Workerorders.html')));

router.get('/worker/income', (req, res) => res.sendFile(path.join(viewPath, 'Workerincome.html')));
router.get('/worker/location', (req, res) => res.sendFile(path.join(viewPath, 'Workerlocation.html')));
router.get('/worker/notifications', (req, res) => res.sendFile(path.join(viewPath, 'Workernotifications.html')));
router.get('/worker/reviews', (req, res) => res.sendFile(path.join(viewPath, 'Workerreviews.html')));
router.get('/worker/settings', (req, res) => res.sendFile(path.join(viewPath, 'Workersettings.html')));
router.get('/service/:type', (req, res) => {
    const type = req.params.type;
    if (type === 'cleaning') res.sendFile(path.join(viewPath, 'Servicecleaning.html'));
    else if (type === 'electric') res.sendFile(path.join(viewPath, 'Serviceelectric.html'));
    else if (type === 'aircon') res.sendFile(path.join(viewPath, 'Serviceaircon.html'));
    else res.status(404).send('Không tìm thấy');
});

// === PUBLIC APIs ===
router.get('/api/services', async (req, res) => {
    try {
        const services = await Service.findAll();
        res.json(services.map(s => ({ service_id: s.service_id, name: s.service_name, description: s.description, price_range: s.base_price, icon: s.icon_url })));
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.get('/api/featured', async (req, res) => {
    try {
        const featured = await FeaturedProvider.findAll();
        res.json(featured.map(f => ({ id: f.id, badge: f.badge, avatar: f.avatar_icon, name: f.provider_name, description: f.description, rating: f.rating, reviewCount: f.review_count, tags: f.tags ? f.tags.split(',') : [], priceText: f.price_text, link: f.service_link })));
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.get('/api/public/providers/:id', async (req, res) => {
    try {
        const p = await Provider.findByPk(req.params.id);
        if (!p) return res.status(404).json({ message: "Không tìm thấy thợ" });
        const reviews = await Review.findAll({ where: { provider_id: p.provider_id } });
        const avg = reviews.length ? reviews.reduce((acc, r) => acc + r.rating_star, 0) / reviews.length : 5.0;
        res.json({ id: p.provider_id, name: p.full_name, bio: p.bio_description || "Chưa có", avatar: p.avatar_url || "👷", verified: p.is_verified, avg_rating: avg.toFixed(1), review_count: reviews.length });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.get('/api/providers/active', async (req, res) => {
    try {
        const { Op } = require('sequelize');
        let serviceQuery = req.query.service;
        let excludePhone = req.query.exclude_phone;
        let whereCondition = { status: 'active', is_verified: true };
        
        if (excludePhone) {
            whereCondition.phone_number = { [Op.ne]: excludePhone };
        }

        if (serviceQuery) {
            let kw = '';
            if (serviceQuery === 'electric') kw = '[Chuyên: Điện nước]';
            else if (serviceQuery === 'cleaning') kw = '[Chuyên: Dọn dẹp]';
            else if (serviceQuery === 'aircon') kw = '[Chuyên: Máy lạnh]';
            
            if (kw) {
                whereCondition.bio_description = { [Op.like]: `%${kw}%` };
            }
        }

        const providers = await Provider.findAll({
            where: whereCondition,
            include: [{ model: Review }]
        });

        res.json(providers.map(p => {
            const distance = (Math.random() * 5 + 0.5).toFixed(1); // Giả lập khoảng cách
            return {
                id: p.provider_id,
                name: p.full_name,
                avatar: p.avatar_url,
                bio: p.bio_description || "Chưa có giới thiệu",
                reviews: p.Reviews ? p.Reviews.length : 0,
                distance: distance
            };
        }));
    } catch (err) {
        console.error("Lỗi lấy danh sách thợ:", err);
        res.status(500).json({ message: "Lỗi server!" });
    }
});

module.exports = router;
