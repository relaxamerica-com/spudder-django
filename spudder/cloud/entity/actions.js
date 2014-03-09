module.exports = function (keys) {
	var krowdio = require('cloud/krowdio');

    return {
        view: function (req, res) {
            var id = req.params.id,
                entityType = req.params.entityType,
                Entity = Parse.Object.extend(entityType),
                query = new Parse.Query(Entity),
                userAgent = req.headers['user-agent'];

            query.get(id, {
                success: function (entity) {
                    function _renderView(team) {
                        var path = 'https://' + keys.getAppName() + '.parseapp.com/public/' + entityType + '/' + id;
                        krowdio.krowdioGetUserMentionActivity(userAgent, entity).then(function(spuds) {
	                        res.render(entityType.toLowerCase() + '/view', {
	                            'displaySponsors' : require('cloud/commons/displaySponsors'),
	                            'entity': entity,
	                            'twitterShareButton': require('cloud/commons/twitterShareButton'),
	                            'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
	                            'facebookShareButton': require('cloud/commons/facebookShareButton'),
	                            'emailShareButton': require('cloud/commons/emailShareButton'),
	                            'meta': {
	                                title: entity.get('name'),
	                                description: entity.get('profile'),
	                                image: entity.get('profileImageThumb') ? entity.get('profileImageThumb') : '',
	                                url: path
	                            },
	                            'returnURL': path,
	                        	'team' : team,
	                        	'spuds' : JSON.parse(spuds),
	                        	'spudContainer' : require('cloud/commons/spudContainer')
	                       });
	                   });
                    }

                    if (entity.get('team')) {
                        entity.get('team').fetch().then(function (_team) {
                            _renderView(_team);
                        });
                    } else {
                       _renderView(null);
                    }
                },
                error: function(object, error) {
                    res.render(entityType.toLowerCase() + '/view');
                }
            });
        }
        
    };
};