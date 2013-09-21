exports.view = function (req, res) {
    res.render('tournament/view', { 
    	'displayItems' : require('cloud/commons/displayItems.js')
	});
};