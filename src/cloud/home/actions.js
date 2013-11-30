exports.home = function (req, res) {
    res.render('home/home', { 'displayItems' : require('cloud/commons/displayItems.js'), 'error' : '' });
};