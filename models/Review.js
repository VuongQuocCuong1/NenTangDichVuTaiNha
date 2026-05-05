const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Review = sequelize.define('Review', {
    review_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    booking_id: { type: DataTypes.INTEGER, allowNull: false },
    user_id: { type: DataTypes.INTEGER, allowNull: false },
    provider_id: { type: DataTypes.INTEGER, allowNull: true },
    rating_star: { type: DataTypes.INTEGER, allowNull: false },
    comment: { type: DataTypes.TEXT }
}, { tableName: 'Reviews', timestamps: false });

module.exports = Review;
