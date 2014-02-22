module.exports = function (app, keys) {
    var spuds = require('cloud/spuds/actions')(keys);
    app.post('/dashboard/createSpud', spuds.createSpud);
};