/** Cloud functions - working as an secure API for Spudder (accessed from Spudmart to obtain information) */

Parse.Cloud.define("team", function(request, response) {
    var teamID = request.params.teamID,
        Team = Parse.Object.extend("Team"),
        query = new Parse.Query(Team),
        teamInfo = {};

    if (!teamID) {
        response.error({'error_code': 400, 'error_message': 'Missing team ID'});
    }


    query.get(teamID).then(function (team) {
        teamInfo = {
            name: team.get('name'),
            image: team.get('profileImageThumb') ? team.get('profileImageThumb') : ''
        };

        response.success(teamInfo);
    }, function (error) {
        response.error({'error_code': 500, 'error_message': error.message});
    });
});

Parse.Cloud.define("team_save_recipient", function(request, response) {
    var teamID = request.params.teamID,
        Team = Parse.Object.extend("Team"),
        query = new Parse.Query(Team);

    if (!teamID) {
        response.error({'error_code': 400, 'error_message': 'Missing team ID'});
    }


    query.get(teamID).then(function (team) {
        team.set('isRegisteredRecipient', true);
        team.save(null, {
            success: function () {
                response.success();
            },

            error: function (team, error) {
                response.error({'error_code': 500, 'error_message': error.message});
            }
        });
    }, function (error) {
        response.error({'error_code': 500, 'error_message': error.message});
    });
});