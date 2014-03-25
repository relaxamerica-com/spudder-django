exports.home = function (req, res) {
    if (Parse.User.current()) {
        return res.redirect('/dashboard');
    }
    res.render('home/home', { 'displayItems' : require('cloud/commons/displayItems.js')});
};