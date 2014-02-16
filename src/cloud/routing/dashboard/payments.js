module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var recipient = require('cloud/dashboard/payments/recipients')(keys);
    app.get('/dashboard/payments/recipient/:teamID', helpers.loginRequired, recipient.register);
    app.get('/dashboard/payments/recipient/:teamID/complete', helpers.loginRequired, recipient.register_complete);
    app.get('/dashboard/payments/recipient/:teamID/thanks', helpers.loginRequired, recipient.register_thanks);
    app.get('/dashboard/payments/recipient/:teamID/error', helpers.loginRequired, recipient.register_error);
};