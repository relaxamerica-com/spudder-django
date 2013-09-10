function equalHeight(group) {
	group.css('min-height', '0px');
	
	var tallest = 0;
	group.each(function() {
		var thisHeight = $(this).height();
		if(thisHeight > tallest) {
			tallest = thisHeight;
		}
	});

	group.css('min-height', tallest + 'px');
	group.css('height', tallest + 'px');
}