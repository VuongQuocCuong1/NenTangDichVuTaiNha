const express = require('express');
const router = express.Router();
const { DirectMessage, User } = require('../models');
const { Op } = require('sequelize');

// Lấy danh sách những người đã nhắn tin với User (Inbox List)
router.get('/:userId/conversations', async (req, res) => {
    try {
        const userId = req.params.userId;

        // Lấy tất cả tin nhắn gửi ĐI hoặc ĐẾN user này
        const messages = await DirectMessage.findAll({
            where: {
                [Op.or]: [
                    { sender_id: userId },
                    { receiver_id: userId }
                ]
            },
            include: [
                { model: User, as: 'Sender', attributes: ['user_id', 'full_name'] },
                { model: User, as: 'Receiver', attributes: ['user_id', 'full_name'] }
            ],
            order: [['created_at', 'DESC']]
        });

        // Nhóm theo người chat
        const conversationMap = new Map();
        
        messages.forEach(msg => {
            // Xác định người kia là ai
            const otherUser = msg.sender_id == userId ? msg.Receiver : msg.Sender;
            if (!otherUser) return;
            
            const otherId = otherUser.user_id;
            if (!conversationMap.has(otherId)) {
                conversationMap.set(otherId, {
                    user_id: otherId,
                    name: otherUser.full_name,
                    last_message: msg.message_text,
                    last_time: msg.created_at
                });
            }
        });

        res.json(Array.from(conversationMap.values()));
    } catch (err) {
        console.error("Lỗi lấy danh sách chat:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// Lấy nội dung chat giữa 2 người
router.get('/:userId/history/:otherId', async (req, res) => {
    try {
        const { userId, otherId } = req.params;

        const messages = await DirectMessage.findAll({
            where: {
                [Op.or]: [
                    { sender_id: userId, receiver_id: otherId },
                    { sender_id: otherId, receiver_id: userId }
                ]
            },
            order: [['created_at', 'ASC']]
        });

        res.json(messages.map(m => ({
            id: m.message_id,
            text: m.message_text,
            is_mine: m.sender_id == userId,
            time: m.created_at
        })));
    } catch (err) {
        console.error("Lỗi lấy lịch sử chat:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// Gửi tin nhắn mới
router.post('/send', async (req, res) => {
    try {
        const { sender_id, receiver_id, text } = req.body;
        
        if (!sender_id || !receiver_id || !text) {
            return res.status(400).json({ message: "Thiếu thông tin gửi." });
        }

        const newMsg = await DirectMessage.create({
            sender_id,
            receiver_id,
            message_text: text
        });

        res.json({ message: "Đã gửi", msg: newMsg });
    } catch (err) {
        console.error("Lỗi gửi tin nhắn:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

module.exports = router;
