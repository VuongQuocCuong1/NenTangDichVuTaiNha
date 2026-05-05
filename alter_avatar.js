const sequelize = require('./config/database');

async function alterTable() {
    try {
        await sequelize.query("ALTER TABLE Users ADD COLUMN avatar_url VARCHAR(255);");
        console.log("✅ Thêm cột 'avatar_url' vào bảng Users thành công!");
    } catch(err) {
        console.log("⚠️ Cột 'avatar_url' đã tồn tại hoặc có lỗi:", err.message);
    }

    try {
        await sequelize.query("ALTER TABLE Providers ADD COLUMN evidence_url VARCHAR(255);");
        console.log("✅ Thêm cột 'evidence_url' vào bảng Providers thành công!");
    } catch(err) {
        console.log("⚠️ Cột 'evidence_url' đã tồn tại hoặc có lỗi:", err.message);
    }
    
    process.exit();
}
alterTable();
