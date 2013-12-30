module.exports = function (app, keys) {
    require('cloud/routing/public')(app, keys);

    require('cloud/routing/accounts')(app, keys);

    require('cloud/routing/dashboard/main')(app, keys);
    require('cloud/routing/dashboard/teams')(app, keys);
    require('cloud/routing/dashboard/amazon')(app, keys);
};