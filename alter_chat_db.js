const sequelize = require('./config/database');

async function createChatTable() {
    try {
        await sequelize.query(`
            CREATE TABLE IF NOT EXISTS DirectMessages (
                message_id INT AUTO_INCREMENT PRIMARY KEY,
                sender_id INT NOT NULL,
                receiver_id INT NOT NULL,
                message_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES Users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES Users(user_id) ON DELETE CASCADE
            );
        `);
        console.log("✅ Đã tạo bảng DirectMessages thành công!");
    } catch(err) {
        console.error("❌ Lỗi:", err);
    } finally {
        process.exit();
    }
}
createChatTable();
