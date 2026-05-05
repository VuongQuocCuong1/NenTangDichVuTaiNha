const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Provider = sequelize.define('Provider', {
    provider_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    full_name: { type: DataTypes.STRING(100), allowNull: false },
    phone_number: { type: DataTypes.STRING(20), unique: true, allowNull: false },
    cccd_number: { type: DataTypes.STRING(20), unique: true },
    avatar_url: { type: DataTypes.STRING(255) },
    evidence_url: { type: DataTypes.STRING(255) },
    bio_description: { type: DataTypes.TEXT },
    is_verified: { type: DataTypes.BOOLEAN, defaultValue: false },
    status: { type: DataTypes.STRING(20), defaultValue: 'inactive' },
    balance: { type: DataTypes.DECIMAL(10, 2), defaultValue: 0 }
}, { tableName: 'Providers', timestamps: false });

module.exports = Provider;
