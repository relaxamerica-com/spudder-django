module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')();
    var _ = require('underscore');

    return {
        list: {
            get: function (req, res) {
                var Team = Parse.Object.extend("Team"),
                    query = new Parse.Query(Team),
                    teamID = req.params.id,
                    offersCount = 0;

                query.get(teamID, {
                    success: function(team) {
                        var TeamOffer = Parse.Object.extend("TeamOffer"),
                            offerQuery = new Parse.Query(TeamOffer),
                            pastOffers = [], currentOffers = [],
                            currentDate = new Date(),
                            currentDateString = currentDate.getFullYear() + '-' +
                                ('0' + (currentDate.getMonth() + 1)).slice(-2) + '-' +
                                ('0' + currentDate.getDate()).slice(-2);

                        offerQuery.equalTo('team', team);

                        offerQuery.find().then(function (offers) {
                            offersCount = offers.length;
                            var promise = Parse.Promise.as();

                            _.each(offers, function(offer) {
                                var endDate = offer.get('endDate');

                                var endDateSplitted = endDate.split('-'),
                                    year = endDateSplitted[0],
                                    month = endDateSplitted[1],
                                    day = endDateSplitted[2];

                                month = ('0' + month).slice(-2);
                                day = ('0' + day).slice(-2);
                                endDate = year + '-' + month + '-' + day;

                                // Database end date format is YYYY-MM-DD, user format is DD-MM-YYYY
                                var revertedEndDate = helpers.revertDate(offer.get('endDate'));
                                offer.set('endDate', revertedEndDate);

                                promise = promise.then(function() {
                                    var findPromise = new Parse.Promise(),
                                        Donation = Parse.Object.extend('Donation'),
                                        donationQuery = new Parse.Query(Donation);

                                    donationQuery.equalTo('offer', offer);

                                    donationQuery.find().then(function (donations) {
                                        offer.set('available', offer.get('quantity') - donations.length);

                                        if (endDate >= currentDateString) {
                                            currentOffers.push(offer);
                                        } else {
                                            pastOffers.push(offer);
                                        }

                                        findPromise.resolve();
                                    });

                                    return findPromise;
                                });
                            });

                            return promise;
                        }).then(function () {
                            res.render('dashboard/teams/offers/list', {
                                'breadcrumbs' : [{ 'title' : 'Teams', 'href' : '/dashboard/teams' }, { 'title' : 'Offers', 'href' : 'javascript:void(0);' }],
                                'team': team,
                                'count': offersCount,
                                'currentOffers': currentOffers,
                                'pastOffers': pastOffers
                            });
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
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Offers', 'href' : '/dashboard/teams/' + team.id + '/offers' },
                                { 'title' : 'Create offer', 'href' : 'javascript:void(0);' }
                            ],
                            'team': team,
                            'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.render('dashboard/teams/offers/list', {
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Offers', 'href' : '/dashboard/teams/' + team.id + '/offers' },
                                { 'title' : 'Error', 'href' : 'javascript:void(0);' }
                            ],
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
                            endDateString = req.body['endDate'], // DD-MM-YYY
                            revertedEndDate = helpers.revertDate(endDateString), // YYYY-MM-DD
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
                        teamOffer.set('endDate', revertedEndDate);
                        teamOffer.set('video', req.body['video']);
                        teamOffer.set('details', req.body['details']);
                        teamOffer.set('team', team);
                        teamOffer.set('images', offerImages);

                        teamOffer.save(null, {
                            success: function () {
                                res.redirect('/dashboard/teams/' + teamID + '/offers');
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
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Offers', 'href' : 'javascript:void(0);' },
                                { 'title' : 'Error', 'href' : 'javascript:void(0);' }
                            ],
                            'list': []
                        });
                    }
                });
            }
        },

        edit: {
            get: function (req, res) {
                var TeamOffer = Parse.Object.extend("TeamOffer"),
                    query = new Parse.Query(TeamOffer),
                    teamID = req.params.teamID,
                    offerID = req.params.offerID;

                query.get(offerID, {
                    success: function(offer) {
                        // Database end date format is YYYY-MM-DD, user format is DD-MM-YYYY
                        var endDate = helpers.revertDate(offer.get('endDate'));
                        offer.set('endDate', endDate);

                        res.render('dashboard/teams/offers/edit', {
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Offers', 'href' : '/dashboard/teams/' + teamID + '/offers' },
                                { 'title' : 'Edit this offer', 'href' : 'javascript:void(0);' }
                            ],
                            'teamID': teamID,
                            'offer': offer,
                            'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID() }
                        });
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.render('dashboard/teams/offers/edit', {
                            'breadcrumbs' : [
                                { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                { 'title' : 'Offers', 'href' : '/dashboard/teams/' + teamID + '/offers' },
                                { 'title' : 'Edit this offer', 'href' : 'javascript:void(0);' }
                            ],
                            'found': false
                        });
                    }
                });
            },

            post: function (req, res) {
                var TeamOffer = Parse.Object.extend('TeamOffer'),
                    query = new Parse.Query(TeamOffer),
                    offerID = req.params.offerID,
                    teamID = req.params.teamID;

                query.get(offerID, {
                    success: function(teamOffer) {
                        var endDateString = req.body['endDate'], // YYYY-MM-DD
                            revertedEndDate = helpers.revertDate(endDateString), // YYYY-MM-DD
                            images = [ req.body['offerImage1'], req.body['offerImage2'], req.body['offerImage3'] ],
                            offerImages = [];

                        for (var i = 0; i < images.length; i++) {
                            if (images[i]) offerImages.push(images[i]);
                        }

                        teamOffer.set('title', req.body['title']);
                        teamOffer.set('phone', req.body['phone']);
                        teamOffer.set('website', req.body['website']);
                        teamOffer.set('quantity', parseInt(req.body['quantity'], 10));
                        teamOffer.set('endDate', revertedEndDate);
                        teamOffer.set('video', req.body['video']);
                        teamOffer.set('details', req.body['details']);

                        if (offerImages) {
                            teamOffer.set('images', offerImages);
                        }

                        teamOffer.save();

                        res.redirect('/dashboard/teams/' + teamID + '/offers/' + offerID + '/edit');
                    },
                    error: function(object, error) {
                        console.log(error);
                        res.redirect('/dashboard/teams/' + teamID + '/offers/' + offerID + '/edit');
                    }
                });
            }
        },

        remove: {
            get: function (req, res) {
                var TeamOffer = Parse.Object.extend("TeamOffer"),
                    query = new Parse.Query(TeamOffer),
                    offerId = req.params.offerID,
                    teamID = req.params.teamID;

                query.get(offerId).then(function (offer) {
                    offer.destroy().then(function () {
                        res.redirect('/dashboard/teams/' + teamID + '/offers');
                    });
                },
                function (error) {
                    console.log(error);
                    res.redirect('/dashboard/teams/' + teamID + '/offers');
                });
            }
        },

        donations: {
            get: function (req, res) {
                var TeamOffer = Parse.Object.extend("TeamOffer"),
                    offerQuery = new Parse.Query(TeamOffer),
                    teamID = req.params.teamID,
                    offerID = req.params.offerID;

                offerQuery.get(offerID, {
                    success: function(offer) {
                        var Donation = Parse.Object.extend('Donation'),
                            donationQuery = new Parse.Query(Donation),
                            donations = [], totalAmount = 0;

                        donationQuery.equalTo('offer', offer);

                        donationQuery.find().then(function (list) {
                            var promise = Parse.Promise.as();

                            _.each(list, function(donation) {
                                promise = promise.then(function() {
                                    var findPromise = new Parse.Promise();

                                    donation.get('sponsor').fetch({
                                        success: function (fetchedSponsor) {
                                            donations.push({
                                                sponsor: fetchedSponsor,
                                                date: donation.createdAt
                                            });

                                            findPromise.resolve();
                                        }
                                    });

                                    return findPromise;
                                });
                            });

                            return promise;
                        }).then(function () {
                            res.render('dashboard/teams/offers/donations', {
                                'breadcrumbs' : [
                                    { 'title' : 'Teams', 'href' : '/dashboard/teams' },
                                    { 'title' : 'Offers', 'href' : '/dashboard/teams/' + teamID + '/offers' },
                                    { 'title' : offer.get('title'), 'href' : '/dashboard/teams/' + teamID + '/offers/' + offerID },
                                    { 'title' : 'Donations', 'href' : 'javascript:void(0);' }
                                ],
                                'offer': offer,
                                'donations': donations,
                                'totalAmount': totalAmount
                            });
                        });
                    }
                });
            }
        }
    };
};