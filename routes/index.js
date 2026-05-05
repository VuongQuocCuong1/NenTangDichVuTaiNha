const express = require('express');
const router = express.Router();

const authRoutes = require('./auth');
const adminRoutes = require('./admin');
const publicRoutes = require('./public');
const bookingsRoutes = require('./bookings');
const providerRoutes = require('./provider');
const userRoutes = require('./user');
const postsRoutes = require('./posts');
const chatRoutes = require('./chat');

router.use('/api/auth', authRoutes);
router.use('/api/admin', adminRoutes);
router.use('/api/bookings', bookingsRoutes);
router.use('/api/provider', providerRoutes);
router.use('/api/user', userRoutes);
router.use('/api/posts', postsRoutes);
router.use('/api/chat', chatRoutes);
router.use('/', publicRoutes); // Mounts /api/public, /api/services, and all HTMLs

module.exports = router;
