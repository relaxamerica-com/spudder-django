module.exports = function (app, keys) {
    var spuds = require('cloud/spuds/actions')(keys),
    	helpers = require('cloud/routing/helpers')();
    	
    app.post('/dashboard/createSpud', helpers.loginRequired, spuds.createSpud);
    app.post('/spuds/comment/:id', spuds.comment);
    app.post('/spuds/toggleLike', spuds.toggleLike);
    app.post('/spuds/encodeTags', helpers.loginRequired, spuds.encodeTags);
    app.post('/spuds/getCommentsPublishers', helpers.loginRequired, spuds.getCommentsPublishers);
    app.get('/spuds/getComments', spuds.getComments);
    app.get('/spuds/getLikes', spuds.getLikes);
    app.get('/spuds/delete/:id', helpers.loginRequired, spuds.deleteSpud);
<<<<<<< HEAD
=======
    app.get('/spuds/getSpuds', helpers.loginRequired, spuds.getSpuds);
>>>>>>> issuesToVerify
};