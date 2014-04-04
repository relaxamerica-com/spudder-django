function buildComment(id, usertext, publisher, createdTime) {
	var comment = $('<div class="comment"></div>'),
		inner = $('<div class="clearfix"></div>'),
		userText = $('<p class="userText"></p>'),
		image = $('<img width="50" height="50" src="/media/dashboard/avatars/no_avatar.png" class="social-avatar pull-left">'),
		profileDetails = $('<div class="profile-details clearfix"></div>'),
		userNameContainer = $('<a href="#" class="user-name">'),
		createdTimeContainer = $('<p><em class="createdTime"></em></p>');
		
	profileDetails.append(userNameContainer);
	profileDetails.append(createdTimeContainer);
	inner.append(image);
	inner.append(profileDetails);
	comment.append(inner);
	comment.append(userText);
	
	comment.attr('id', id);			

	userText.html(usertext);
	
	if (publisher.profileImageThumb.length > 0) {
		image.attr('src', publisher.profileImageThumb);
	}
	
	var userName = 'Annonymous';
		
	if (publisher.nickname.length > 0) {
		userName = publisher.nickname;
	} else if (publisher.krowdioUserId.length > 0) {
		userName = publisher.krowdioUserId;
	}
	
	userNameContainer.html(userName);
	userNameContainer.attr('href', '/public/fan/' + publisher.id);
	
	
	var date = createdTime instanceof Date ? createdTime : new Date(createdTime),
		convertedDate = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
	
	createdTimeContainer.find('.createdTime').html(convertedDate);
	
	return comment;
}

function teamTagExists(spudContainer) {
	var decodedTags = spudContainer.find('.decodedTags').val(),
		doesExist = false,
		id = null;
	
	$.each(decodedTags.split(' '), function() {
		var tag = this.toString();
		if (tag.match(/^@Team.*$/)) {
			id = tag.replace('@Team', '');
				
			spudContainer.find('.tag-buttons .btn').attr('alreadyTagged', 'true');
			doesExist = true;
			return false;
		}
	});
	
	return { 
		doesExist: doesExist,
		id: id
	};
}

function setTeamPlayersAndCoaches(teamId, spudContainer) {
	var response = $.get('/getTeamPlayersAndCoaches', { 'id' : teamId });
	
	response.done(function(data) {
		var selectPlayers = $('<select team="' + teamId + '"></select>'),
			selectCoaches = $('<select team="' + teamId + '"></select>'),
			parsed = JSON.parse(data);
			
		$.each(parsed.players, function() {
			var option = $('<option></option>');
			
			option.attr('value', this.objectId);
			option.html(this.name);
			selectPlayers.append(option);
		});
		
		$.each(parsed.coaches, function() {
			var option = $('<option></option>');
			
			option.attr('value', this.objectId);
			option.html(this.name);
			selectCoaches.append(option);
		});
		
		spudContainer.find('.tag-coach .inputs').append(selectCoaches);
		spudContainer.find('.tag-player .inputs').append(selectPlayers);
	});
}

function getEntityPublicViewURL(clazz, id) {
	if (clazz == 'Team') {
		return '/teams/' + id;
	}
	if (clazz == 'Player' || clazz == 'Coach') {
		return '/public/' + clazz + '/' + id;
	}
	if (clazz == 'User') {
		return '/public/fan/' + id; 
	}
}

function addTag(entityType, entityId, entityName, spudContainer) {
	var tags = $(spudContainer).find('.tags-container'),
		tagSpan = $('<span class="tag">'),
		tagsInput = $(spudContainer).find('input.tags'),
		tagsInputValue = tagsInput.val();
			
	if (!tags.is(':visible')) {
		tags.show();
	}
	
	tagSpan.html( '<a href="">' + entityName + '</a>' );
	tags.append( tagSpan );
	tagsInput.val( tagsInputValue + (tagsInputValue.length > 0 ? ' ' : '') + '@' + entityType + entityId );
}

function setTeamIdByName(name, requestId, spudContainer) {
	var _name = name,
		loading = showLoading(spudContainer.find('.tagTeam')),
		deferred = new $.Deferred(),
		idHasBeenSetDeferred = new $.Deferred();
	
	if (requestId) {
		$.get('/getTeamIdByName', { 'name' : name }).done(function(data) {
			var entity = JSON.parse(data);
			
			if ( entity.exists ) {
				deferred.resolve(entity.id);
			} else {
				alert('The Team with the given name does NOT exists.', spudContainer);	
			}
		});
	} else {
		deferred.resolve(spudContainer.find('.tag-team select').val());
	}
	
	deferred.promise().then(function(entityId) {
		addTag('Team', entityId, _name, spudContainer);
		
		loading.end();
		
		idHasBeenSetDeferred.resolve(entityId);
	});
	
	return idHasBeenSetDeferred.promise();
}

function showLoading(container) {
	var deferred = new $.Deferred(),
		previousValue = $(container).html(),
		spinner = $('<img src="/media/img/ajax-loader-orange.gif" />');
	
	deferred.promise().then(function() {
		$(container).html(previousValue);
	});
	
	$(container).html(spinner);
	
	deferred.end = function() {
		deferred.resolve();
	};
	
	return deferred;
}

$('.btn.like').hover(function() {
    $(this).find('img').attr('src', '/media/img/ajax-loader-dark-grey.gif');
}, function() {
    $(this).find('img').attr('src', '/media/img/ajax-loader.gif');
});

function applyAddCommentListener(user) {
	var _user = user;
	
	$('.spud-container .add-comment').on('submit', function(e) {
		e.preventDefault();
		
		var url = $(this).attr('action'),
			commentInput = $(this).find('input[name="comment"]'),
			text = commentInput.val(),
			self = this,
			postingComment = $(this).find('.posting-comment'),
			spudContainer = $(this).parents('.spud-container'),
			self = this;
			
		postingComment.css('display', 'inline-block');
		commentInput.val('');
		
		var response = $.post(url, { 'comment' : text });
		
		response.done(function() {
			
			var comment = buildComment('', text, _user, new Date().toString());
			
			$(self).find('.load-more').after(comment);
			
			comment.show();
			comment.animate({
				opacity: 1
			}, 2000);
			
			postingComment.hide();
			
		});
		
		response.fail(function(data) {
			if (JSON.parse(data).statusCode == 401) {
				document.location = '/accounts/loginOrRegister?next=' + document.location.pathname;
			}
		});
	});
}

function getEntityIdFromURL() {
	var parsed = $.url(document.location).data.attr.path.split('/');
	
	return parsed[parsed.length - 1];
}

function overwriteListeners() {
	$('.buttons-bottom .btn').off('click');
	$('.buttons-bottom .btn').click(function(e) {
		e.preventDefault();
		e.stopPropagation();
		
		document.location = '/accounts/loginOrRegister?next=' + document.location.pathname;
	});
}

function applyPopulateCommentsListener(entityType) {
	$('.spud-container .spud-comments .load-more').click(function() {
		var nextPage = $(this).attr('nextPage');
		populateComments(nextPage, entityType);
	});

    $('[name="comment"]').click(function() {
        var currentComments = $('.spud-container:visible .comment');

        if (!currentComments.length) {
	        populateComments(1, entityType);
        } else if (!currentComments.is(':visible')) {
        	currentComments.show();
        	currentComments.animate({
        		opacity: 1
        	}, 2000);
        }
    });
}

function populateComments(page, entityType) {
	var spudContainer = $('.spud-container:visible'),
		spudComments = spudContainer.find('.spud-comments'),
		loading = spudContainer.find('.loading-comments'),
		spudId = spudContainer.attr('id'),
		loadMoreComments = spudContainer.find('.spud-comments .load-more'),
		page = parseInt(page, 10);
		
	loading.css('display', 'table');
	
	var response = $.get('/spuds/getComments', {
		'spudId' : spudId,
		'entityId' : getEntityIdFromURL(),
		'page' : page,
		'entityType' : entityType
	});
	
	response.done(function(data) {
		var parsed = JSON.parse(data),
			comments = parsed.data;

        if (comments.length) {
            spudContainer.find('.load-comments').html(parsed.totalItems + ' comments');
        }
        
        // comments = comments.sort(function(a, b) { return new Date(a.created_time) - new Date(b.created_time); });

		$.each(comments, function() {
			if ($('#' + this._id).length == 0) {
				var comment = $('<div class="comment"></div>'),
					inner = $('<div class="clearfix"></div>'),
					userText = $('<p class="userText"></p>'),
					image = $('<img width="50" height="50" src="/media/dashboard/avatars/no_avatar.png" class="social-avatar pull-left">'),
					profileDetails = $('<div class="profile-details clearfix"></div>'),
					userNameContainer = $('<a href="#" class="user-name">'),
					createdTime = $('<p><em class="createdTime"></em></p>');
		
				profileDetails.append(userNameContainer);
				profileDetails.append(createdTime);
				inner.append(image);
				inner.append(profileDetails);
				comment.append(inner);
				comment.append(userText);
				
				comment.attr('id', this._id);			

				userText.html(this.usertext);
				
				if (this.publisher.profileImageThumb.length > 0) {
					image.attr('src', this.publisher.profileImageThumb);
				}
				
				var userName = 'Annonymous';
					
				if (this.publisher.nickname.length > 0) {
					userName = this.publisher.nickname;
				} else if (this.publisher.krowdioUserId.length > 0) {
					userName = this.publisher.krowdioUserId;
				}
				
				userNameContainer.html(userName);
				userNameContainer.attr('href', '/public/fan/' + this.publisher.id);
				
				var date = this.created_time;
				
				date = new Date(date);
        		data = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
				
				createdTime.find('.createdTime').html(data);
				
				loadMoreComments.after(comment);
				
				comment.animate({
					opacity: 1
				}, 2000);
				comment.show();
			}
		});
		
		if (parsed.pagination.next) {
			loadMoreComments.css('display', 'table');
			loadMoreComments.attr('nextPage', page + 1);
		} else { 
			loadMoreComments.hide();
			loadMoreComments.attr('nextPage', 'null');
		}
		
		loading.hide();
	});
	
	response.fail(function() {
		loading.hide();
	});
}

function getLikes(entityType) {
    var spudContainer = $('.spud-container:visible'),
        spudId = spudContainer.attr('id'),
        loadingLikes = spudContainer.find('.loading-likes'),
        existingCounter = spudContainer.find('.like-counter');

	console.log(spudId);

    var response = $.get('/spuds/getLikes', {
        'spudId' : spudId,
        'entityId' : getEntityIdFromURL(),
        'entityType' : entityType
    });

    if (existingCounter.length) {
        existingCounter.hide();
    }
    loadingLikes.css('display', 'inline-block');

    response.done(function(data) {
        var parsed = JSON.parse(data),
            counter = existingCounter.length ? existingCounter : $('<span class="like-counter"></span>');

        counter.html(parsed.totalItems);

        if (existingCounter.length == 0) {
            spudContainer.find('.like').prepend(counter);
        }

        counter.show();
        loadingLikes.hide();
    });
}


