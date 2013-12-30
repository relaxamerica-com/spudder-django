var EJS = require('ejs');
var fs = require('fs');

module.exports = function(text) {
    return EJS.render(fs.readFileSync('cloud/views/commons/share/twitter.ejs'), { 'tweet_text': text });
};