const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const FeaturedProvider = sequelize.define('FeaturedProvider', {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    badge: { type: DataTypes.STRING(50) },
    avatar_icon: { type: DataTypes.STRING(255) },
    provider_name: { type: DataTypes.STRING(100) },
    description: { type: DataTypes.STRING(255) },
    rating: { type: DataTypes.FLOAT, defaultValue: 5.0 },
    review_count: { type: DataTypes.INTEGER, defaultValue: 0 },
    tags: { type: DataTypes.STRING(255) },
    price_text: { type: DataTypes.STRING(100) },
    service_link: { type: DataTypes.STRING(255) }
}, { tableName: 'FeaturedProviders', timestamps: false });

module.exports = FeaturedProvider;
