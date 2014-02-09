module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var recipient = require('cloud/dashboard/sponsor/recipients')(keys);
    app.get('/dashboard/recipient/:teamID', helpers.loginRequired, recipient.recipient);
    app.get('/dashboard/recipient/:teamID/complete', helpers.loginRequired, recipient.recipient_complete);

    var donations = require('cloud/dashboard/sponsor/donations')(keys);
    app.get('/dashboard/sponsor', helpers.loginRequired, donations.donations);
    app.get('/dashboard/sponsor/:teamID/:offerID', helpers.loginRequired, donations.sponsor);
    app.get('/dashboard/sponsor/complete', helpers.loginRequired, donations.sponsor_complete);

    var page = require('cloud/dashboard/sponsor/page')(keys);
    app.get('/dashboard/sponsor/page', helpers.loginRequired, page.manage.get);
    app.post('/dashboard/sponsor/page', helpers.loginRequired, page.manage.post);
};