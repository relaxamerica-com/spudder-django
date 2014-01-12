module.exports = function (keys) {
    return {
        spuds: function (req, res) {
            var breadcrumbs = [{ 'title' : 'SPUDS', 'href' : '/dashboard' }];
            res.render('dashboard/spuds', {
                'breadcrumbs' : breadcrumbs
            });
        },

        mySpuds: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/spuds' }, { 'title' : 'My Spuds', 'href' : '/dashboard/fans/spuds' }];
        	res.render('dashboard/fan/mySpuds', {
                'breadcrumbs' : breadcrumbs,
                'modalTop' : require('cloud/dashboard/fan/modalTop'),
                'modalBottom' : require('cloud/dashboard/fan/modalBottom'),
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        myFavorites: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/favorites' }, { 'title' : 'My Favorites', 'href' : '/dashboard/fans/favorites' }];
        	res.render('dashboard/fan/myFavorites', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
            });
        },
        
        basicInfo: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/basicInfo' }, { 'title' : 'Basic Info', 'href' : '/dashboard/fans/basicInfo' }];
        	res.render('dashboard/fan/basicInfo', {
                'breadcrumbs' : breadcrumbs,
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        settings: function(req, res) {
        	var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Settings', 'href' : '/dashboard/fans/settings' }];
        	res.render('dashboard/fan/settings', {
                'breadcrumbs' : breadcrumbs,
            });
        }
        
    };
};