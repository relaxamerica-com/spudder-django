module.exports = function (keys) {
    return {
        spuds: function (req, res) {
            var breadcrumbs = ['SPUDS'];
            res.render('dashboard/spuds', {
                'breadcrumbs' : breadcrumbs
            });
        },

        general: function (req, res) {
            var breadcrumbs = ['Fans', 'General'];
            res.render('dashboard/fan/general', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
                'modalTop' : require('cloud/dashboard/fan/modalTop'),
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        mySpuds: function(req, res) {
        	var breadcrumbs = ['Fans', 'My Spuds'];
        	res.render('dashboard/fan/mySpuds', {
                'breadcrumbs' : breadcrumbs,
                'modalTop' : require('cloud/dashboard/fan/modalTop'),
            });
        },
        
        myFavorites: function(req, res) {
        	var breadcrumbs = ['Fans', 'My Favorites'];
        	res.render('dashboard/fan/myFavorites', {
                'breadcrumbs' : breadcrumbs,
                'displayUsers' : require('cloud/commons/displayUsers'),
            });
        },
        
        basicInfo: function(req, res) {
        	var breadcrumbs = ['Fans', 'Basic Info'];
        	res.render('dashboard/fan/basicInfo', {
                'breadcrumbs' : breadcrumbs,
                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
            });
        },
        
        settings: function(req, res) {
        	var breadcrumbs = ['Fans', 'Settings'];
        	res.render('dashboard/fan/settings', {
                'breadcrumbs' : breadcrumbs,
            });
        }
    };
};