module.exports = function (keys) {
    var _ = require('underscore');

    function getSponsorName(sponsor) {
        var sponsorName = '';

        if (sponsor.get('name')) sponsorName = sponsor.get('name');
        if (sponsor.get('lastName')) sponsorName += sponsor.get('lastName');

        if (!sponsor.get('name') && !sponsor.get('lastName')) {
            sponsorName = sponsor.get(sponsor.get('nickname') ? 'nickname' : 'username');
        }
        return sponsorName;
    }

    function getSponsorImage(sponsorPage, sponsor) {
        var thumbnail = '';

        if (sponsorPage.get('thumbnail')) {
            thumbnail = sponsorPage.get('thumbnail')
        } else if (sponsor.get('profileImageThumb')) {
            thumbnail = sponsor.get('profileImageThumb');
        }
        return thumbnail;
    }

    function setLocationExternalLink(sponsorPage) {
        if (sponsorPage.get('location')) {
            var mapInfo = sponsorPage.get('mapInfo'),
                startIndex = mapInfo.indexOf('href="') + 6,
                endIndex = mapInfo.indexOf(' target') - 1,
                link = mapInfo.substring(startIndex, endIndex);

            sponsorPage.set('externalLink', link);
        }
    }

    return {
        view: function (req, res) {
            var sponsorID = req.params.id;
            var Sponsor = Parse.Object.extend('User'),
                sponsorQuery = new Parse.Query(Sponsor);

            sponsorQuery.get(sponsorID, {
                success: function(sponsor) {
                    var SponsorPage = Parse.Object.extend('SponsorPage'),
                        sponsorPageQuery = new Parse.Query(SponsorPage);

                    sponsorPageQuery.equalTo('sponsor', sponsor);

                    sponsorPageQuery.first({
                        success: function(sponsorPage) {
                            function isAlreadyAdded (teams, team) {
                                for (var  i = 0; i < teams.length; i++) {
                                    if (teams[i].id == team.id) return true;
                                }

                                return false;
                            }

                            var sponsorName = getSponsorName(sponsor),
                                image = getSponsorImage(sponsorPage, sponsor),
                                path = 'https://' + keys.getAppName() + '.parseapp.com/sponsors/' + sponsorID;

                            setLocationExternalLink(sponsorPage);

                            var SponsoredTeams = Parse.Object.extend('SponsoredTeams'),
                                query = new Parse.Query(SponsoredTeams),
                                teams = [];

                            query.equalTo('sponsor', sponsor);

                            query.find().then(function (list) {
                                var promise = Parse.Promise.as();

                                if (list.length) {
                                    return list[0].relation('teams').query().find();
                                }

                                return promise;
                            }).then(function (sponsored_teams) {
                                teams = sponsored_teams ? sponsored_teams : [];
                            }).then(function () {
                                res.render('sponsors/view', {
                                    'displayTeams' : require('cloud/commons/displayTeams'),
                                    'sponsor': sponsor,
                                    'page': sponsorPage,
                                    'teams': teams,
                                    'twitterShareButton': require('cloud/commons/twitterShareButton'),
                                    'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
                                    'facebookShareButton': require('cloud/commons/facebookShareButton'),
                                    'emailShareButton': require('cloud/commons/emailShareButton'),
                                    'meta': {
                                        title: sponsorName,
                                        description: sponsorPage.get('description'),
                                        image: image,
                                        url: path
                                    },
                                    'returnURL': path
                                });
                            });
                        },
                        error: function(error) {
                            console.log("Error: " + error.code + " " + error.message);
                        }
                    });
                }
            });
        }
    };
};