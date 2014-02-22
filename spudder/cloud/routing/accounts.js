module.exports = function (app, keys) {
    var accounts = require('cloud/accounts/actions')(keys),
    	helpers = require('cloud/routing/helpers')();

    app.post('/accounts/login', accounts.login);
    app.post('/accounts/register', accounts.register);
    app.get('/accounts/logout', accounts.logout);
    app.post('/accounts/editProfile', helpers.loginRequired, accounts.editProfile);
    
};