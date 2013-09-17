module.exports = function (keys) {
    Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());

    return {
        login: function(req, res) {
            Parse.User.logIn(req.body.username, req.body.password, {
                success: function(user) {
                    res.redirect('/');
                },
                error: function(user, error) {
                    console.log('error occured');
                }
            });
        },

        logout: function(req, res) {
            Parse.User.logOut();
            res.redirect('/');
        }
    }
};