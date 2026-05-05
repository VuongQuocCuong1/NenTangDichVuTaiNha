const { DataTypes, Sequelize } = require('sequelize');
const sequelize = require('../config/database');
const User = require('./User');

const DirectMessage = sequelize.define('DirectMessage', {
    message_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    sender_id: { type: DataTypes.INTEGER, allowNull: false, references: { model: User, key: 'user_id' } },
    receiver_id: { type: DataTypes.INTEGER, allowNull: false, references: { model: User, key: 'user_id' } },
    message_text: { type: DataTypes.TEXT, allowNull: false },
    created_at: { type: DataTypes.DATE, defaultValue: Sequelize.NOW }
}, { tableName: 'DirectMessages', timestamps: false });

module.exports = DirectMessage;
