const { DataTypes, Sequelize } = require('sequelize');
const sequelize = require('../config/database');

const ChatMessage = sequelize.define('ChatMessage', {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    booking_id: { type: DataTypes.INTEGER, allowNull: false },
    sender_type: { type: DataTypes.STRING(20) },
    message: { type: DataTypes.TEXT, allowNull: false },
    created_at: { type: DataTypes.DATE, defaultValue: Sequelize.NOW }
}, { tableName: 'chat_message', timestamps: false });

module.exports = ChatMessage;
