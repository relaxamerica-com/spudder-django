$(document).ready(function() {
	$('.dialogs, .comments').slimScroll({
		height: '300px'
	});
	
	$(".navigation-buttons .btn, .spud-container .btn").tooltip({
		track: true,
		hide: {
			effect: "explode",
			delay: 2500,
			duration: 5000
		},
		show: {
			effect: "slideDown",
			delay: 2500,
			duration: 5000
		}
	});
	
	$('#toggle-chat').click(function() {
		var chat = $('.chat-wrapper');
		
		if ( chat.is(':visible') ) {
			$(chat).addClass('hidden');
		} else {
			$(chat).removeClass('hidden');
		}
	});
	
	$('#spud-carousel').carousel({
		interval: false
	});
	
	$('#spud-carousel').on('slid', function() {
        getLikes();
	});
	
	function populateComments() {
		var spudContainer = $('.spud-container:visible'),
			spudComments = spudContainer.find('.spud-comments'),
			loading = spudContainer.find('.loading-comments'),
			spudId = spudContainer.attr('id');
			
		loading.css('display', 'table');
		
		var response = $.get('/spuds/getComments', {
			'spudId' : spudId
		});
		
		response.done(function(data) {
			var comments = JSON.parse(data);

            if (comments.length) {
                $('.load-comments').html(comments.length + ' comments');
            }
            
            comments = comments.sort(function(a, b) { return new Date(b.created_time) - new Date(a.created_time); });

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
					
					spudComments.append(comment);
					comment.show();
				}
			});
			
			loading.hide();
		});
		
		response.fail(function() {
			loading.hide();
		});
	}

    $('[name="comment"]').click(function() {
        var currentComments = $('.spud-container .comment');

        if (!currentComments.length) {
	        populateComments();
        } else if (!currentComments.is(':visible')) {
        	currentComments.show();
        }
    });

    function getLikes() {
        var spudContainer = $('.spud-container:visible'),
            spudId = spudContainer.attr('id'),
            loadingLikes = spudContainer.find('.loading-likes'),
            existingCounter = spudContainer.find('.like-counter');

        var response = $.get('/spuds/getLikes', {
            'spudId' : spudId
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

	$('.load-comments').click(function() {
		var currentComments = $('.spud-container:visible .comment');
		
		if (currentComments.is(':visible')) {
			currentComments.hide();
		} else {
			currentComments.show();
		}
	});

    getLikes();

	$('.btn.like').click(function() {
		var spudContainer = $(this).parents('.spud-container'),
			spudID = spudContainer.attr('id'),
			loadingLikes = spudContainer.find('.loading-likes'),
			counter = spudContainer.find('.like-counter');
			
		var response = $.post('/spuds/toggleLike', {
			'id' : spudID
		});
		
		loadingLikes.css('display', 'inline-block');
		counter.hide();
		
		response.done(function(data) {
			var parsed = JSON.parse(data);
			loadingLikes.hide();
            counter.html(parsed.totalItems);
			counter.css('display', 'inline-block');
		});
	});

    $('.tag').click(function() {
        var spudContainer = $(this).parents('.spud-container'),
            buttons = spudContainer.find('.tag-buttons'),
            decodedTags = spudContainer.find('.decodedTags'),
            teamExists = teamTagExists(spudContainer),
            isAlreadyLoaded = $(this).hasClass('alreadyLoaded'),
            self = this;

        if (teamExists.doesExist && !isAlreadyLoaded) {
            setTeamPlayersAndCoaches(teamExists.id, spudContainer);
        }

        if (buttons.is(':visible')) {
            buttons.hide();
        } else {
            buttons.show();
        }

        var tagsContainer = $(decodedTags).parents('.spud-container').find('.tags-container'),
            tags = $(decodedTags).val();

        if (tags.length && !isAlreadyLoaded) {

            var loadingTags = $(spudContainer).find('.loading-tags');

            loadingTags.show();

            $.post('/spuds/encodeTags', {
                'tags' : $(decodedTags).val()
            }, function(httpResponse) {
                var tags = JSON.parse(httpResponse).items;

                $(self).addClass('alreadyLoaded');

                $.each(tags, function() {
                    var tagDiv = $('<div class="tag"></div>'),
                        tagLink = $('<a href=""></a>');

                    tagLink.attr('href', getEntityPublicViewURL(this.clazz, this.id));
                    tagLink.html(this.name);
                    tagDiv.html(tagLink);

                    tagsContainer.append(tagDiv);
                });

                loadingTags.hide();
            });

        }

    });

    $('.tag-buttons .btn').click(function() {
        var title = $(this).attr('data-original-title').toLowerCase(),
            spudContainer = $(this).parents('.spud-container'),
            inputs = spudContainer.find('.tag-' + title);

        if (title == 'team' && $(this).attr('alreadyTagged') == 'true') {
            alert('You can tag only one Team per SPUD.', spudContainer);
            return;
        }

        if (inputs.is(':visible')) {
            inputs.hide();
        } else {
            inputs.show();
        }

    });

    function alert(msg, spudContainer) {
        var alert = spudContainer.find('.alert-danger');
        alert.html(
            msg
        );

        alert.show();
    }
    
    $('.tagTeam').click(function(e) {
		e.preventDefault();
		
		var nameFromInput = $(this).parent().find('input').val(),
			select = $(this).parent().find('select'),
			idFromSelect = select.val(),
			nameFromSelect = select.find(':selected').html(),
			name = idFromSelect.length > 0 ? nameFromSelect : nameFromInput,
			spudContainer = $(this).parents('.spud-container');
		
		if (nameFromInput.length == 0 && idFromSelect.length == 0) {
			alert('You must select a team from favorites or type name of the existing team', spudContainer);
		}
			
		setTeamIdByName(name, nameFromInput.length > 0, spudContainer).then(function(teamId) {
			setTeamPlayersAndCoaches(teamId, spudContainer);
			$('.tag-team').hide();
			spudContainer.find('[data-original-title="Team"]').attr('alreadyTagged', 'true');
		});
		
		
	}); 
	
	$('.tagPlayer').click(function(e) {
		e.preventDefault();
		
		var selected = $(this).parent().find('select').find(':selected');
		
		addTag('Player', selected.val(), selected.html(), $(this).find('.spud-container'));
	});
	
	$('.tagCoach').click(function(e) {
		e.preventDefault();
		
		var selected = $(this).parent().find('select').find(':selected');
		
		addTag('Coach', selected.val(), selected.html(), $(this).find('.spud-container'));
	});
	

});