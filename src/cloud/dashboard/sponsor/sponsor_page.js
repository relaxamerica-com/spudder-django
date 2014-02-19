module.exports = function (keys) {
    var helpers = require('cloud/teams/helpers')();
    var _ = require('underscore');

    return {
        manage: {
            get: function (req, res) {
                Parse.User.current().fetch().then(function(sponsor) {
                    var SponsorPage = Parse.Object.extend('SponsorPage'),
                        sponsorPageQuery = new Parse.Query(SponsorPage);

                    sponsorPageQuery.equalTo('sponsor', sponsor);

                    sponsorPageQuery.find({
                        success: function (results) {
                            var page = results.length ? results[0] : undefined,
                                mapInfo = page ? page.get('mapInfo') : undefined,
                                lat, lng, infoWindow;

                            if (mapInfo) {
                                var splitted = mapInfo.split(';');

                                lat = splitted[0];
                                lng = splitted[1];
                                infoWindow = splitted[2];
                            }

                            res.render('dashboard/sponsors/page/manage', {
                                'breadcrumbs' : [
                                    { 'title' : 'Sponsors', 'href' : '/dashboard/sponsor' },
                                    { 'title' : 'Sponsor page', 'href' : 'javascript:void(0);' }
                                ],
                                'page': page,
                                'lat': lat,
                                'lng': lng,
                                'infoWindow': infoWindow,
                                'keys' : { 'jsKey' : keys.getJavaScriptKey(), 'appId' : keys.getApplicationID(), 'placesAPIKey': keys.getGooglePlacesAPIKey() }
                            });
                        },

                        error: function (error) {
                            console.log(error);
                        }
                    })
                });
            },

            post: function (req, res) {
                Parse.User.current().fetch().then(function(sponsor) {
                    var imageInputs = [ req.body['offerImage1'], req.body['offerImage2'], req.body['offerImage3'] ],
                        locationInfo = [req.body['infoLat'], req.body['infoLng'], req.body['infoWindow']].join(';'),
                        images = [];

                    for (var i = 0; i < imageInputs.length; i++) {
                        if (imageInputs[i]) images.push(imageInputs[i]);
                    }

                    var SponsorPage = Parse.Object.extend('SponsorPage'),
                        sponsorPageQuery = new Parse.Query(SponsorPage);

                    sponsorPageQuery.equalTo('sponsor', sponsor);

                    sponsorPageQuery.find({
                        success: function (results) {
                            var sponsorPage = results.length ? results[0] : new SponsorPage();

                            sponsorPage.set('sponsor', sponsor);
                            sponsorPage.set('name', req.body['name']);
                            sponsorPage.set('speciality', req.body['speciality']);
                            sponsorPage.set('phone', req.body['phone']);
                            sponsorPage.set('fax', req.body['fax']);
                            sponsorPage.set('email', req.body['email']);
                            sponsorPage.set('description', req.body['description']);
                            sponsorPage.set('website', req.body['website']);
                            sponsorPage.set('video', req.body['video']);
                            sponsorPage.set('location', req.body['location']);
                            sponsorPage.set('mapInfo', locationInfo);
                            sponsorPage.set('thumbnail', req.body['thumbnail']);
                            sponsorPage.set('images', images);

                            sponsorPage.save(null, {
                                success: function () {
                                    res.redirect('/dashboard/sponsor/page');
                                },

                                error: function (team, error) {
                                    console.log(error);
                                }
                            });
                        }
                    });
                });
            }
        }
    }
};