$(document).ready(function() {
	$('form#basicInfoForm button[type="submit"]').click(function(e) {
		e.preventDefault();
		
		var form = $('form#basicInfoForm'),
			avatar = form.find('#avatarURL'),
			fileUploadControl = $("#profile-avatar-input")[0];
		
		if (fileUploadControl.files.length > 0) {
			var file = fileUploadControl.files[0],
				name = file.name;
			var parseFile = new Parse.File(name, file);
			parseFile.save().then(function(image) {
				avatar.val(image.url());
				$(form).submit();
			}, function(error) {
				console.log(error);
			});
		} else {
			$(form).submit();
		}
	});
	
	$("#basic_info .input-required").tooltip({
		hide: {
			effect: "explode",
			delay: 2500
		},
		show: {
			effect: "slideDown",
			delay: 2500
		}
	});
				
	$('#profile-avatar-input').ace_file_input({
		no_file:'No File ...',
		btn_choose:'Choose',
		btn_change:'Select',
		droppable:false,
		onchange:null,
		thumbnail:true, //| true | large
		whitelist:'gif|png|jpg|jpeg',
		blacklist:'exe|php'
		//onchange:''
		//
	});
});