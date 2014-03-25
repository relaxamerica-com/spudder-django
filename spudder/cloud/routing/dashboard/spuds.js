module.exports = function (app, keys) {
    var spuds = require('cloud/spuds/actions')(keys),
    	helpers = require('cloud/routing/helpers')();
    	
    app.post('/dashboard/createSpud', helpers.loginRequired, spuds.createSpud);
    app.post('/spuds/comment/:id', helpers.loginRequired, spuds.comment);
    app.post('/spuds/toggleLike', helpers.loginRequired, spuds.toggleLike);
    app.post('/spuds/encodeTags', helpers.loginRequired, spuds.encodeTags);
    app.post('/spuds/getCommentsPublishers', helpers.loginRequired, spuds.getCommentsPublishers);
    app.get('/spuds/getComments', spuds.getComments);
    app.get('/spuds/getLikes', spuds.getLikes);
};