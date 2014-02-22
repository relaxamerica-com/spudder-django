module.exports = function (app, keys) {
    var helpers = require('cloud/routing/helpers')(),
    	entity = require('cloud/dashboard/entity/actions')(keys);
    
    app.get('/dashboard/createEntity/:entityType/:teamId', helpers.loginRequired, entity.createEntity.get);
    app.get('/dashboard/createEntity/:entityType', helpers.loginRequired, entity.createEntity.get);
    app.post('/dashboard/createEntity/:entityType', helpers.loginRequired, entity.createEntity.post);
    app.get('/dashboard/listEntities/:entityType', helpers.loginRequired, entity.listEntities);
    app.get('/dashboard/editEntity/:entityType/:id', helpers.loginRequired, entity.editEntity.get);
    app.post('/dashboard/editEntity/:entityType/:id', helpers.loginRequired, entity.editEntity.post);
    app.get('/dashboard/removeEntity/:entityType/:id', helpers.loginRequired, entity.removeEntity);
    app.post('/dashboard/removeAdmin/:entityType/:id', helpers.loginRequired, entity.removeAdmin);
    app.get('/acceptEntityInvitation/:entityInvitationId', helpers.loginRequired, entity.acceptEntityInvitation);
    app.get('/rejectEntityInvitation/:entityInvitationId', entity.rejectEntityInvitation);
    app.get('/invitationsList', helpers.loginRequired, entity.invitationsList);
};