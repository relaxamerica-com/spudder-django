exports.offer = function (req, res) {
    var teamID = req.params.teamID,
        offerID = req.params.offerID;

    console.log("Team ID: " + teamID);
    console.log("Offer ID: " + offerID);

    var Team = Parse.Object.extend("Team"),
        query = new Parse.Query(Team);

    query.get(teamID, {
        success: function(team) {
            var TeamOffer = Parse.Object.extend('TeamOffer'),
                offerQuery = new Parse.Query(TeamOffer);

            offerQuery.get(offerID,{
                success: function(offer) {
                    res.render('teams/offer/offer', {
                        'displayItems' : require('cloud/commons/displayItems.js'),
                        'team': team,
                        'offer': offer
                    });

                },
                error: function(object, error) {
                    console.log('Error fetching Offer');
                    console.log(error);
                    res.render('teams/offer/error');
                }
            });
        },
        error: function(object, error) {
            console.log('Error fetching Team');
            console.log(error);
            res.render('teams/offer/error');
        }
    });
};