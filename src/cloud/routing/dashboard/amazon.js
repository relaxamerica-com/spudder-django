module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var amazon = require('cloud/dashboard/amazon')(keys);

    app.get('/dashboard/recipient/:teamID', helpers.loginRequired, amazon.recipient);
    app.get('/dashboard/recipient/:teamID/complete', helpers.loginRequired, amazon.recipient_complete);

    app.get('/dashboard/sponsor', helpers.loginRequired, amazon.donations);
    app.get('/dashboard/sponsor/:teamID/:offerID', helpers.loginRequired, amazon.sponsor);
    app.get('/dashboard/sponsor/complete', helpers.loginRequired, amazon.sponsor_complete);

};