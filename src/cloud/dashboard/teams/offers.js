module.exports = function () {
    return {
        list: {
            get: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id;

                query.get(teamID, {
                    success: function(team) {
                        res.render('dashboard/teams/offers/list', {
                            'breadcrumbs' : ['Teams', team.get('name'), 'Offers'],
                            'list': []
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.render('dashboard/teams/offers/list', {
                            'breadcrumbs' : ['Teams', 'Error'],
                            'list': []
                        });
                    }
                });
            }
        }
    }
};