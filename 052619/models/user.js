const mongoose = require('mongoose');

let userSchema = new mongoose.Schema({
    username: String,
    name: String,
    dateCrawled: Date
});

let User = mongoose.model('User', userSchema);

module.exports = User;