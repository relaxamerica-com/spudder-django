module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var dashboard = require('cloud/dashboard/actions')(keys);
    app.get('/dashboard', helpers.loginRequired, dashboard.spuds);

    app.get('/dashboard/fans/spuds', helpers.loginRequired, dashboard.mySpuds);
    app.get('/dashboard/fans/favorites', helpers.loginRequired, dashboard.myFavorites);
    app.get('/dashboard/fans/settings', helpers.loginRequired, dashboard.settings);
    app.get('/dashboard/fans/basicInfo', helpers.loginRequired, dashboard.basicInfo);

    var amazon = require('cloud/dashboard/fan/amazon')(keys);
    app.get('/dashboard/fans/amazon/connect', helpers.loginRequired, amazon.connect);
    app.get('/dashboard/fans/amazon/connect_complete', helpers.loginRequired, amazon.connect_complete);
    app.get('/dashboard/fans/amazon/connected', helpers.loginRequired, amazon.connected);
    app.get('/dashboard/fans/amazon/disconnect', helpers.loginRequired, amazon.disconnect.get);
    app.post('/dashboard/fans/amazon/disconnect', helpers.loginRequired, amazon.disconnect.post);
    app.get('/dashboard/fans/amazon/disconnected', helpers.loginRequired, amazon.disconnected);
};