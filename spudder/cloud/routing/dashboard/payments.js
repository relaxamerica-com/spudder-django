module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var payments = require('cloud/dashboard/payments/actions')(keys);
    app.get('/dashboard/payments/recipient/:teamID', helpers.loginRequired, payments.recipient);
    app.get('/dashboard/payments/donate/:teamID/:offerID', helpers.loginRequired, payments.donation);
};