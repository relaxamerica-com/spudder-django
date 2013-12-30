module.exports = function (keys) {

    return {
        view: function (req, res) {
            var id = req.params.id,
            	entityType = req.params.entityType,
                Entity = Parse.Object.extend(entityType),
                query = new Parse.Query(Entity);

            query.get(id, {
                success: function (entity) {
					function _renderView(team) {
	                    var path = 'https://' + keys.getAppName() + '.parseapp.com/public/' + entityType + '/' + id;
	                    res.render(entityType.toLowerCase() + '/view', {
	                        'displaySponsors' : require('cloud/commons/displaySponsors'),
	                        'entity': entity,
	                        'twitterShareButton': require('cloud/commons/twitterShareButton'),
	                        'googlePlusShareButton': require('cloud/commons/googlePlusShareButton'),
	                        'facebookShareButton': require('cloud/commons/facebookShareButton'),
	                        'meta': {
	                            title: entity.get('name'),
	                            description: entity.get('profile'),
	                            image: entity.get('profileImageThumb') ? team.get('profileImageThumb') : '',
	                            url: path
	                        },
	                        'returnURL': path,
	                        'team' : team
	                	});
                	}
                	
                	if (entity.get('team')) {
	                	var Team = Parse.Object.extend('Team'),
	                		teamQuery = new Parse.Query(Team);
	                		
	                	teamQuery.equalTo('name', entity.get('team'));
	                	
	                	teamQuery.first().then(function(team) {
	                		_renderView(team);
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