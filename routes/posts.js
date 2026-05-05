const express = require('express');
const router = express.Router();
const path = require('path');
const multer = require('multer');
const { Post, PostComment, User } = require('../models');

// Cấu hình multer - tối đa 500MB, hỗ trợ ảnh và video
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, 'static/uploads/'),
    filename: (req, file, cb) => cb(null, 'post_' + Date.now() + path.extname(file.originalname))
});
const upload = multer({
    storage,
    limits: { fileSize: 500 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        const allowed = /jpeg|jpg|png|gif|webp|mp4|mov|avi|webm/;
        const ext = path.extname(file.originalname).toLowerCase().slice(1);
        if (allowed.test(ext)) cb(null, true);
        else cb(new Error('Chỉ hỗ trợ ảnh (jpg, png, gif) và video (mp4, mov, webm)!'));
    }
});

// --- LẤY TẤT CẢ BÀI ĐĂNG ---
router.get('/', async (req, res) => {
    try {
        const posts = await Post.findAll({
            order: [['created_at', 'DESC']],
            include: [
                { model: User, attributes: ['user_id', 'full_name'] },
                {
                    model: PostComment,
                    include: [{ model: User, attributes: ['user_id', 'full_name'] }]
                }
            ]
        });
        res.json(posts);
    } catch (err) {
        console.error("Lỗi lấy bài đăng:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// --- ĐĂNG BÀI MỚI ---
router.post('/', upload.single('media'), async (req, res) => {
    try {
        const { user_id, content } = req.body;
        if (!user_id) return res.status(400).json({ message: "Thiếu thông tin người dùng!" });
        if (!content && !req.file) return res.status(400).json({ message: "Bài đăng phải có nội dung hoặc ảnh/video!" });

        const user = await User.findByPk(user_id);
        if (!user) return res.status(404).json({ message: "Không tìm thấy người dùng" });

        let media_url = null, media_type = null;
        if (req.file) {
            media_url = '/static/uploads/' + req.file.filename;
            const videoExts = ['mp4', 'mov', 'avi', 'webm'];
            const ext = path.extname(req.file.originalname).toLowerCase().slice(1);
            media_type = videoExts.includes(ext) ? 'video' : 'image';
        }

        const post = await Post.create({ user_id, content: content ? content.trim() : null, media_url, media_type });

        const result = await Post.findByPk(post.post_id, {
            include: [
                { model: User, attributes: ['user_id', 'full_name'] },
                { model: PostComment }
            ]
        });
        res.status(201).json(result);
    } catch (err) {
        console.error("Lỗi đăng bài:", err);
        res.status(500).json({ message: err.message || "Lỗi Server" });
    }
});

// --- BÌNH LUẬN ---
router.post('/:postId/comments', async (req, res) => {
    try {
        const { user_id, content } = req.body;
        if (!user_id || !content || !content.trim()) return res.status(400).json({ message: "Thiếu nội dung bình luận!" });
        const post = await Post.findByPk(req.params.postId);
        if (!post) return res.status(404).json({ message: "Không tìm thấy bài đăng" });
        const comment = await PostComment.create({ post_id: req.params.postId, user_id, content: content.trim() });
        const result = await PostComment.findByPk(comment.comment_id, {
            include: [{ model: User, attributes: ['user_id', 'full_name'] }]
        });
        res.status(201).json(result);
    } catch (err) {
        console.error("Lỗi bình luận:", err);
        res.status(500).json({ message: "Lỗi Server" });
    }
});

// --- LIKE ---
router.post('/:postId/like', async (req, res) => {
    try {
        const post = await Post.findByPk(req.params.postId);
        if (!post) return res.status(404).json({ message: "Không tìm thấy bài đăng" });
        post.likes_count = (post.likes_count || 0) + 1;
        await post.save();
        res.json({ likes_count: post.likes_count });
    } catch (err) { res.status(500).json({ message: "Lỗi Server" }); }
});

// --- XÓA BÀI ---
router.delete('/:postId', async (req, res) => {
    try {
        const { user_id } = req.body;
        const post = await Post.findByPk(req.params.postId);
        if (!post) return res.status(404).json({ message: "Không tìm thấy bài đăng" });
        if (post.user_id !== parseInt(user_id)) return res.status(403).json({ message: "Bạn không có quyền xóa bài này!" });
        await PostComment.destroy({ where: { post_id: req.params.postId } });
        await post.destroy();
        res.json({ message: "Đã xóa bài đăng thành công!" });
    } catch (err) { res.status(500).json({ message: "Lỗi Server" }); }
});

module.exports = router;
