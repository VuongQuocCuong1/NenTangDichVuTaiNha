const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const PostComment = sequelize.define('PostComment', {
    comment_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    post_id: { type: DataTypes.INTEGER, allowNull: false },
    user_id: { type: DataTypes.INTEGER, allowNull: false },
    content: { type: DataTypes.TEXT, allowNull: false },
    created_at: { type: DataTypes.DATE, defaultValue: DataTypes.NOW }
}, { tableName: 'PostComments', timestamps: false });

module.exports = PostComment;
