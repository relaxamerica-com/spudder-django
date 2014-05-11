function saving(btn, alert, msg) {
	var dfd = new $.Deferred();

	$(btn).html(window.preloadedBlack);
	$(btn).on('mouseleave', function() {
		$(btn).html(window.preloadedOrange);
	});
	$(btn).addClass('saving');

	dfd.promise().then(function() {
		$(btn).html('Save');
		$(btn).removeClass('saving');
		$(btn).off('mouseleave');
		showAlert(alert, msg, 'success', true);
	});

	return dfd;
}

function showAlert(alert, msg, type, isAutoHide) {
	$(alert).html(msg);
	$(alert).addClass('alert-' + type);
	$(alert).css({
		'display' : 'block'
	});

	if (isAutoHide) {
		setTimeout(function() {
			$(alert).animate({
				'opacity' : '0'
			}, 2000, function() {
				$(alert).css({
					'display' : 'none',
					'opacity' : '1'
				});
			});
		}, 2000);
	}
}