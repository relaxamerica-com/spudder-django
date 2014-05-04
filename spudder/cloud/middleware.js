module.exports = function (app, keys) {
    function getInvites(user) {
        var Invitation = Parse.Object.extend('EntityInvitation'),
            invQuery = new Parse.Query(Invitation);

        return invQuery.equalTo('invited', user).find();
    }

    app.use(function(req, res, next){
        Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());
        var currentUser = Parse.User.current();
        if (currentUser) {
            currentUser.fetch().then(function(user) {
                res.locals.user = user;
                getInvites(user).then(function(invites) {
                    res.locals.invites = invites;
                    next();
                });
            });
        } else {
            res.locals.user = null;
            next();
        }
    });

    app.use(function(req, res, next) {
        res.locals.getValueOrEmpty = function(value) {
            return value ? value : '';
        };

        res.locals.getEntityName = function(entity) {
            try {
                if (entity.get('isDisplayPublicly')) {
                    name = entity.get('name');
                } else {
                    name = entity.get('publicName');
                }
                return name;
            } catch(error) {
                return '';
            }
        };

        next();
    });

    // Basic information that are different on each server
    app.use(function(req, res, next) {
        res.locals.loginWithAmazonClientID = keys.getLoginWithAmazonClientID();
        res.locals.baseURL = keys.getBaseURL();
        next();
    });
};