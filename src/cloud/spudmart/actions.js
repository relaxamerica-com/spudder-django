exports.view = function (req, res) {
    res.render('spudmart/home', { 'displayItems' : require('cloud/commons/displayItems.js') });
};

exports.offer = function (req, res) {
    res.render('spudmart/offer/offer', { 'displayItems' : require('cloud/commons/displayItems.js') });
};