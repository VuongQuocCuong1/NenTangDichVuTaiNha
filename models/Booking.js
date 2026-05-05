const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Booking = sequelize.define('Booking', {
    booking_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    user_id: { type: DataTypes.INTEGER },
    provider_id: { type: DataTypes.INTEGER, allowNull: true },
    service_id: { type: DataTypes.INTEGER },
    package_name: { type: DataTypes.STRING(100) },
    total_amount: { type: DataTypes.DECIMAL(10, 2) },
    service_address: { type: DataTypes.TEXT, allowNull: false },
    scheduled_time: { type: DataTypes.DATE, allowNull: false },
    status: { type: DataTypes.STRING(20), defaultValue: 'pending' }
}, { tableName: 'Bookings', timestamps: false });

module.exports = Booking;
