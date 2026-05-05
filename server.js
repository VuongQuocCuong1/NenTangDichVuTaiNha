const express = require('express');
const cors = require('cors');
const path = require('path');
const { sequelize } = require('./models');
const routes = require('./routes');

const app = express();
app.use(cors());
app.use(express.json({ limit: '500mb' }));
app.use(express.urlencoded({ limit: '500mb', extended: true }));

// Serve static files
app.use('/static', express.static(path.join(__dirname, 'static')));

// === KẾT NỐI DATABASE MYSQL ===
sequelize.authenticate()
    .then(() => console.log('✅ Đã kết nối MySQL qua Sequelize thành công!'))
    .catch(err => console.error('❌ Lỗi kết nối MySQL:', err));

// === SỬ DỤNG ROUTES ===
app.use('/', routes);

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`🚀 Server Node.js đang chạy tại http://127.0.0.1:${PORT}`);
});
