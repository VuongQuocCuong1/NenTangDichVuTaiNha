const sequelize = require('../config/database');

const User = require('./User');
const Provider = require('./Provider');
const Service = require('./Service');
const Booking = require('./Booking');
const Review = require('./Review');
const ChatMessage = require('./ChatMessage');
const WalletTransaction = require('./WalletTransaction');
const FeaturedProvider = require('./FeaturedProvider');
const Post = require('./Post');
const PostComment = require('./PostComment');
const DirectMessage = require('./DirectMessage');

// --- Relationships ---
Booking.belongsTo(User, { foreignKey: 'user_id' });
Booking.belongsTo(Service, { foreignKey: 'service_id' });
Booking.belongsTo(Provider, { foreignKey: 'provider_id' });
User.hasMany(Booking, { foreignKey: 'user_id' });
Provider.hasMany(Booking, { foreignKey: 'provider_id' });

Review.belongsTo(User, { foreignKey: 'user_id' });
Review.belongsTo(Provider, { foreignKey: 'provider_id' });
Review.belongsTo(Booking, { foreignKey: 'booking_id' });
Provider.hasMany(Review, { foreignKey: 'provider_id' });

WalletTransaction.belongsTo(Provider, { foreignKey: 'provider_id' });

Post.belongsTo(User, { foreignKey: 'user_id' });
User.hasMany(Post, { foreignKey: 'user_id' });
PostComment.belongsTo(User, { foreignKey: 'user_id' });
PostComment.belongsTo(Post, { foreignKey: 'post_id' });
Post.hasMany(PostComment, { foreignKey: 'post_id' });

DirectMessage.belongsTo(User, { as: 'Sender', foreignKey: 'sender_id' });
DirectMessage.belongsTo(User, { as: 'Receiver', foreignKey: 'receiver_id' });
User.hasMany(DirectMessage, { as: 'SentMessages', foreignKey: 'sender_id' });
User.hasMany(DirectMessage, { as: 'ReceivedMessages', foreignKey: 'receiver_id' });

module.exports = {
    sequelize,
    User,
    Provider,
    Service,
    Booking,
    Review,
    ChatMessage,
    WalletTransaction,
    FeaturedProvider,
    Post,
    PostComment,
    DirectMessage
};
