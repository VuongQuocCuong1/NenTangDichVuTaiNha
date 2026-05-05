const { DataTypes, Sequelize } = require('sequelize');
const sequelize = require('../config/database');

const WalletTransaction = sequelize.define('WalletTransaction', {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    provider_id: { type: DataTypes.INTEGER },
    amount: { type: DataTypes.DECIMAL(10, 2) },
    transaction_type: { type: DataTypes.STRING(20) },
    description: { type: DataTypes.STRING(255) },
    created_at: { type: DataTypes.DATE, defaultValue: Sequelize.NOW }
}, { tableName: 'WalletTransactions', timestamps: false });

module.exports = WalletTransaction;
