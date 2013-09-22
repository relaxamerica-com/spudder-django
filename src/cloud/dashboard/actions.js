exports.spuds = function (req, res) {
	var breadcrumbs = ['SPUDS'];
    res.render('dashboard/spuds', {
    	'breadcrumbs' : breadcrumbs
    });
};

exports.general = function (req, res) {
	var breadcrumbs = ['Fans', 'General'];
    res.render('dashboard/fan/general', {
    	'breadcrumbs' : breadcrumbs,
    	'displayUsers' : require('cloud/commons/displayUsers'),
    	'modalTop' : require('cloud/dashboard/fan/modalTop')
    });
};