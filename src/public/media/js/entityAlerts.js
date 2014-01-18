$(document).ready(function() {
	var hash = document.location.hash.replace('#', '');
	if (hash == 'accepted') {
		$('.alert').addClass('alert-success');
		$('.alert').show();
		$('.alert').html('Invitation accepted');
		$('.alert').alert();
	}
	if (hash == 'rejected') {
		$('.alert').addClass('alert-danger');
		$('.alert').show();
		$('.alert').html('Invitation rejected');
		$('.alert').alert();
	}
});
