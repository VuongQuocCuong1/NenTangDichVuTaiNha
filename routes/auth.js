const express = require('express');
const router = express.Router();
const { User } = require('../models');
const bcrypt = require('bcryptjs');
const nodemailer = require('nodemailer');
const { Op } = require('sequelize');

const otp_storage = {};

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: 'lenlao570@gmail.com', pass: 'raqvoaszjkdmjqlv' }
});

function sendOtpEmail(receiverEmail, otp) {
    return new Promise((resolve) => {
        const mailOptions = {
            from: 'lenlao570@gmail.com',
            to: receiverEmail,
            subject: 'Mã xác nhận OTP - Khôi phục mật khẩu NTDVhome',
            html: `<div style="padding: 20px; border: 1px solid #ddd; text-align: center;"><h2>Mã OTP của bạn là: ${otp}</h2></div>`
        };
        transporter.sendMail(mailOptions, (err) => resolve(!err));
    });
}

router.post('/register', async (req, res) => {
    try {
        const { fullName, phone, email, password } = req.body;
        const existingUser = await User.findOne({ where: { [Op.or]: [{ phone_number: phone }, { email }] } });
        if (existingUser) return res.status(400).json({ message: "Số điện thoại hoặc Email đã được đăng ký!" });
        const hashedPassword = await bcrypt.hash(password, 10);
        await User.create({ full_name: fullName, phone_number: phone, email, password_hash: hashedPassword });
        res.status(201).json({ message: "Đăng ký thành công!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

router.post('/login', async (req, res) => {
    try {
        const { phone, email, password } = req.body;
        const loginId = phone || email;
        const user = await User.findOne({ where: { [Op.or]: [{ phone_number: loginId }, { email: loginId }] } });
        if (!user) return res.status(401).json({ message: "Thông tin đăng nhập không chính xác!" });
        const isMatch = await bcrypt.compare(password, user.password_hash);
        if (!isMatch && password !== user.password_hash) return res.status(401).json({ message: "Mật khẩu không chính xác!" });
        res.status(200).json({ token: "fake-jwt", user: { id: user.user_id, email: user.email, name: user.full_name, phone: user.phone_number, role: user.role } });
    } catch (err) { res.status(500).json({ message: "Lỗi server" }); }
});

router.post('/forgot-password', async (req, res) => {
    try {
        const { email } = req.body;
        const user = await User.findOne({ where: { email } });
        if (!user) return res.status(404).json({ message: "Email không tồn tại!" });
        const otp = Math.floor(100000 + Math.random() * 900000).toString();
        const expires = new Date(); expires.setMinutes(expires.getMinutes() + 5);
        otp_storage[email] = { otp, expires };
        const success = await sendOtpEmail(email, otp);
        if (success) res.status(200).json({ message: "Gửi OTP thành công!" });
        else res.status(500).json({ message: "Lỗi gửi mail!" });
    } catch (err) { res.status(500).json({ message: "Lỗi Server" }); }
});

router.post('/verify-otp', (req, res) => {
    const { email, otp } = req.body;
    const stored = otp_storage[email];
    if (!stored || new Date() > stored.expires || stored.otp !== otp) return res.status(400).json({ message: "Mã OTP không hợp lệ hoặc hết hạn!" });
    res.status(200).json({ message: "Xác thực OTP thành công!" });
});

router.post('/reset-password', async (req, res) => {
    try {
        const { email, newPassword } = req.body;
        const user = await User.findOne({ where: { email } });
        if (!user) return res.status(404).json({ message: "Lỗi!" });
        user.password_hash = await bcrypt.hash(newPassword, 10);
        await user.save();
        delete otp_storage[email];
        res.status(200).json({ message: "Đổi mật khẩu thành công!" });
    } catch (err) { res.status(500).json({ message: "Lỗi server!" }); }
});

module.exports = router;
