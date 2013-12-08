module.exports = function (keys) {
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
                            'team': team,
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
        },

        create: {
            get: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id;

                query.get(teamID, {
                    success: function(team) {
                        res.render('dashboard/teams/offers/create', {
                            'breadcrumbs' : ['Teams', team.get('name'), 'Offers', 'Create offer'],
                            'team': team,
                            'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
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
            },

            post: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id;

                query.get(teamID, {
                    success: function(team) {
                        var TeamOffer = Parse.Object.extend('TeamOffer'),
                            teamOffer = new TeamOffer(),
                            dateString = req.body['endDate'],
                            dateRegExp = /(\d{4})-(\d{2})-(\d{2})/,
                            endDateArray = dateRegExp.exec(dateString),
                            endDate = new Date(
                                (+endDateArray[1]),
                                (+endDateArray[2] - 1), // Months starts from 0!
                                (+endDateArray[3]),
                                0, 0, 0 // Hours, minutes and seconds
                            ),
                            images = [ req.body['offerImage1'], req.body['offerImage2'], req.body['offerImage3'] ],
                            offerImages = [];

                        for (var i = 0; i < images.length; i++) {
                            if (images[i]) offerImages.push(images[i]);
                        }

                        teamOffer.set('title', req.body['title']);
                        teamOffer.set('donation', req.body['donation']);
                        teamOffer.set('phone', req.body['phone']);
                        teamOffer.set('website', req.body['website']);
                        teamOffer.set('quantity', parseInt(req.body['quantity'], 10));
                        teamOffer.set('endDate', endDate);
                        teamOffer.set('video', req.body['video']);
                        teamOffer.set('details', req.body['details']);
                        teamOffer.set('team', team);
                        teamOffer.set('images', offerImages);

                        teamOffer.save(null, {
                            success: function () {
                                res.redirect('/dashboard/teams/Th4D76dUdZ/offers');
                            },

                            error: function (team, error) {
                                console.log(error);
//                                res.redirect('/dashboard/teams/create?error' + encodeURIComponent(error));
                            }
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