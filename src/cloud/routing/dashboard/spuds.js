module.exports = function (app, keys) {
    var spuds = require('cloud/spuds/actions')(keys),
    	helpers = require('cloud/routing/helpers')();
    	
    app.post('/dashboard/createSpud', helpers.loginRequired, spuds.createSpud);
};