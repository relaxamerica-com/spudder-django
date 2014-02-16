module.exports = function (keys) {
    return {
        list_donations: function (req, res) {
            var _ = require('underscore');

            Parse.User.current().fetch().then(function (user) {
                var Donation = Parse.Object.extend('Donation'),
                    query = new Parse.Query(Donation),
                    donations = [], totalAmount = 0;

                query.equalTo('sponsor', user);
                query.descending('createdAt');

                query.find().then(function (list) {
                    var promise = Parse.Promise.as();

                    _.each(list, function(donation) {
                        promise = promise.then(function() {
                            var findPromise = new Parse.Promise();

                            var offer = donation.get('offer'),
                                team = donation.get('team');

                            offer.fetch({
                                success: function (fetchedOffer) {
                                    team.fetch({
                                        success: function (fetchedTeam) {
                                            donations.push({
                                                offer: fetchedOffer,
                                                team: fetchedTeam,
                                                date: donation.createdAt
                                            });

                                            totalAmount += parseFloat(fetchedOffer.get('donation'));

                                            findPromise.resolve();
                                        }
                                    });
                                }
                            });

                            return findPromise;
                        });
                    });

                    return promise;
                }).then(function () {
                        res.render('dashboard/sponsors/list_donations', {
                            'breadcrumbs' : [
                                { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                                { 'title' : 'My donations', 'href' : 'javascript:void(0);' }
                            ],
                            'donations': donations,
                            'totalAmount': totalAmount
                        });
                    });
            });
        }
    }
};