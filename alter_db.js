const sequelize = require('./config/database');

async function alterTable() {
    try {
        await sequelize.query("ALTER TABLE Users ADD COLUMN bio TEXT;");
        console.log("✅ Thêm cột 'bio' thành công!");
    } catch(err) {
        if(err.name === 'SequelizeDatabaseError' && err.message.includes('Duplicate column name')) {
            console.log("✅ Cột 'bio' đã tồn tại từ trước.");
        } else {
            console.error("❌ Lỗi:", err);
        }
    } finally {
        process.exit();
    }
}
alterTable();
