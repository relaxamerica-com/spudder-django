module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var donations = require('cloud/dashboard/sponsor/donations')(keys);
    app.get('/dashboard/sponsor', helpers.loginRequired, donations.list_donations);

    var page = require('cloud/dashboard/sponsor/sponsor_page')(keys);
    app.get('/dashboard/sponsor/page', helpers.loginRequired, page.manage.get);
    app.post('/dashboard/sponsor/page', helpers.loginRequired, page.manage.post);
};