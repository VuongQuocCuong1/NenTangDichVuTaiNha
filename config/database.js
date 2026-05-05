const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('ntdvhome_db', 'root', '123456', {
    host: 'localhost',
    dialect: 'mysql',
    logging: false // Tắt log SQL để terminal đỡ rối
});

module.exports = sequelize;
