const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const User = sequelize.define('User', {
    user_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    full_name: { type: DataTypes.STRING(100), allowNull: false },
    phone_number: { type: DataTypes.STRING(20), unique: true, allowNull: false },
    email: { type: DataTypes.STRING(100), unique: true },
    password_hash: { type: DataTypes.STRING(255), allowNull: false },
    role: { type: DataTypes.STRING(20), defaultValue: 'user' },
    default_address: { type: DataTypes.TEXT },
    bio: { type: DataTypes.TEXT },
    avatar_url: { type: DataTypes.STRING(255) }
}, { tableName: 'Users', timestamps: false });

module.exports = User;
