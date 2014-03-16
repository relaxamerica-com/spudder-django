module.exports = function () {
    return {
        loginRequired: function (req, res, next) {
            var currentUser = Parse.User.current();
            if (!currentUser) {
                res.redirect('/accounts/login');
            } else {
                return next();
            }
        }
    };
};