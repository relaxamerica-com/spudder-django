module.exports = function (app, keys) {
    var accounts = require('cloud/accounts/actions')(keys);

    app.post('/accounts/login', accounts.login);
    app.post('/accounts/register', accounts.register);
    app.get('/accounts/logout', accounts.logout);
    app.post('/accounts/editProfile', accounts.editProfile);
};