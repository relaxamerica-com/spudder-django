$(document).ready(function() {
	var hash = document.location.hash.replace('#', '');
	
	function alert(clazz, msg) {
		$('.alert').addClass(clazz);
		$('.alert').show();
		$('.alert').html(msg);
		$('.alert').alert();
	}
	
	if (hash == 'invitationAccepted') {
		alert('alert-success', 'The invitation accepted');
	}
	if (hash == 'invitationRejected') {
		alert('alert-danger', 'The invitation rejected');
	}
	if (hash == 'invitationSent') {
		alert('alert-success', 'The invitations have been sent.');
	}
});
