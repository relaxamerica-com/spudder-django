module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var dashboard = require('cloud/dashboard/actions')(keys);
    app.get('/dashboard', helpers.loginRequired, dashboard.spuds);

    app.get('/dashboard/fans/spuds', helpers.loginRequired, dashboard.mySpuds);
    app.get('/dashboard/fans/favorites', helpers.loginRequired, dashboard.myFavorites);
    app.get('/dashboard/fans/settings', helpers.loginRequired, dashboard.settings);
    app.get('/dashboard/fans/basicInfo', helpers.loginRequired, dashboard.basicInfo);
};