$(document).ready(function() {
	var spudId = $.url(document.location).data.param.query['spudId'];
    if (spudId) {
    	$('.item').removeClass('active');
    	$('#' + spudId).parent('.item').addClass('active');
    }
	
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
	
	$('#spud-carousel').on('slide', function() {
		$('.comment').css({
			'opacity' : '0',
			'display' : 'none'
		});
		$('.spud-comments .load-more').hide();
	});
	
	$('.load-comments').click(function() {
		var spudContainer = $('.spud-container:visible'),
			currentComments =  spudContainer.find('.comment'),
			lastComment = spudContainer.find('.comment:last'),
			loadMoreComments = spudContainer.find('.spud-comments .load-more');
		
		if (currentComments.is(':visible')) {
			currentComments.hide();
			loadMoreComments.hide();
			lastComment.after(loadMoreComments);
		} else {
			if (loadMoreComments.attr('nextPage') != 'null') {
				loadMoreComments.show();
			}
			currentComments.show();
        	currentComments.animate({
        		opacity: 1
        	}, 2000);
        	lastComment.after(loadMoreComments);
		}
	});

	$('.btn.like').click(function() {
		var spudContainer = $(this).parents('.spud-container'),
			spudID = spudContainer.attr('id'),
			loadingLikes = spudContainer.find('.loading-likes'),
			counter = spudContainer.find('.like-container');
			
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
		
		response.fail(function(data) {
			if (JSON.parse(data).statusCode == 401) {
				document.location = '/accounts/loginOrRegister?next=' + document.location.pathname;
			}
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