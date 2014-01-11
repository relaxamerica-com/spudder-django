module.exports = function () {
    return {
        loginRequired: function (req, res, next) {
            var currentUser = Parse.User.current();
            if (!currentUser) {
                res.redirect('/?next=' + req.url + '#mySignin');
            } else {
                return next();
            }
        }
    };
};