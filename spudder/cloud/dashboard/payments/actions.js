module.exports = function (keys) {
    return {
        recipient: function (req, res) {
            Parse.User.current().fetch().then(function (user) {
                var teamID = req.params.teamID,
                    connectedWithAmazon = user.get('amazonID') != '',
                    spudmartURL = keys.getSpudmartURL() + '/dashboard/recipient/' + teamID;

                res.render('dashboard/payments/recipient', {
                    'breadcrumbs': [
                        { 'title': 'Teams', 'href': '/dashboard/teams' },
                        { 'title': 'Registering as Recipient', 'href': 'javascript:void(0);' }
                    ],
                    'spudmartURL': spudmartURL,
                    'teamID': teamID,
                    'connected': connectedWithAmazon
                });
            });
        }
    };
};