$(document).ready(function() {
	var allSwitch = $('#accordion2 input[name="switch-field-all"]');
	var switches = $('#accordion2 input[name!="switch-field-all"]');
	
	allSwitch.click(function() {
		$.each(switches, function() {
			if ( $(allSwitch).attr('checked') == 'checked' ) {
				$(this).attr('checked', 'checked');
			} else {
				$(this).removeAttr('checked');
			}
		});
	});
});