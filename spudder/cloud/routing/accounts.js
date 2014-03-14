module.exports = function (app, keys) {
    var accounts = require('cloud/accounts/actions')(keys),
        helpers = require('cloud/routing/helpers')();

    app.get('/accounts/login', accounts.login.get);
    app.post('/accounts/login', accounts.login.post);
    app.get('/accounts/amazon_login', accounts.login_with_amazon);
    app.get('/accounts/register', accounts.register.get);
    app.post('/accounts/register', accounts.register.post);
    app.get('/accounts/amazon_register', accounts.register_with_amazon);
    app.get('/accounts/logout', accounts.logout);
    app.post('/accounts/editProfile', helpers.loginRequired, accounts.editProfile);
    
};