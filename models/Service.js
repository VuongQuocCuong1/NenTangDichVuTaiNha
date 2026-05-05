const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Service = sequelize.define('Service', {
    service_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    service_name: { type: DataTypes.STRING(100), allowNull: false },
    description: { type: DataTypes.TEXT },
    base_price: { type: DataTypes.DECIMAL(10, 2) },
    icon_url: { type: DataTypes.STRING(255) }
}, { tableName: 'Services', timestamps: false });

module.exports = Service;
