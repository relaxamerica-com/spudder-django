// middleware allowing to use user in template
module.exports = function (app, keys) {
    app.use(function(req, res, next){
        Parse.initialize(keys.getApplicationID(), keys.getJavaScriptKey());
        var currentUser = Parse.User.current();
        if (currentUser) {
            currentUser.fetch().then(function(user) {
                res.locals.user = user;
                next();
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
};