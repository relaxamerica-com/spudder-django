function checkEmailsExists(emails) {
	jQuery.ajaxSetup({ async: false });
	
	var response = $.get('/checkEmailsExists', { 'emails' : emails }),
		notFoundEmails = [];
	
	response.done(function(data) {
		notFoundEmails = JSON.parse(data)['notFoundEmails'];
	});
	
	jQuery.ajaxSetup({ async: true });
	
	return notFoundEmails;
}
