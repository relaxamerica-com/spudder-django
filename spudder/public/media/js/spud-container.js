$(document).ready(function() {
	$('.dialogs,.comments').slimScroll({
		height: '300px'
	});
	
	$.each($("div.bar div.button, div.spud-container div.button"), function() {
		$(this).tooltip({
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
	})
	
	$('#toggle-chat').click(function() {
		var chat = $('.chat-wrapper');
		
		if ( chat.is(':visible') ) {
			$(chat).addClass('hidden');
		} else {
			$(chat).removeClass('hidden');
		}
	});
});