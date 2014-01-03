module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')();

    var dashboard = require('cloud/dashboard/actions')(keys);
    app.get('/dashboard', helpers.loginRequired, dashboard.spuds);
    app.get('/dashboard/general', helpers.loginRequired, dashboard.general);

    app.get('/dashboard/fans/spuds', helpers.loginRequired, dashboard.mySpuds);
    app.get('/dashboard/fans/favorites', helpers.loginRequired, dashboard.myFavorites);
    app.get('/dashboard/fans/settings', helpers.loginRequired, dashboard.settings);
    app.get('/dashboard/fans/basicInfo', helpers.loginRequired, dashboard.basicInfo);
    
    app.get('/dashboard/createEntity/:entityType/:teamId', helpers.loginRequired, dashboard.createEntity.get);
    app.get('/dashboard/createEntity/:entityType', helpers.loginRequired, dashboard.createEntity.get);
    app.post('/dashboard/createEntity/:entityType', helpers.loginRequired, dashboard.createEntity.post);
    app.get('/dashboard/listEntities/:entityType', helpers.loginRequired, dashboard.listEntities);
    app.get('/dashboard/editEntity/:entityType/:id', helpers.loginRequired, dashboard.editEntity.get);
    app.post('/dashboard/editEntity/:entityType/:id', helpers.loginRequired, dashboard.editEntity.post);
    app.get('/dashboard/removeEntity/:entityType/:id', helpers.loginRequired, dashboard.removeEntity);
    app.post('/dashboard/removeAdmin/:entityType/:id', helpers.loginRequired, dashboard.removeAdmin);
};