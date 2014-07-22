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