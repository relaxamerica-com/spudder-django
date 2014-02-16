module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var donations = require('cloud/dashboard/sponsor/donations')(keys);
    app.get('/dashboard/sponsor', helpers.loginRequired, donations.donations);
    app.get('/dashboard/sponsor/:teamID/:offerID', helpers.loginRequired, donations.sponsor);
    app.get('/dashboard/sponsor/complete', helpers.loginRequired, donations.sponsor_complete);

    var page = require('cloud/dashboard/sponsor/page')(keys);
    app.get('/dashboard/sponsor/page', helpers.loginRequired, page.manage.get);
    app.post('/dashboard/sponsor/page', helpers.loginRequired, page.manage.post);
};