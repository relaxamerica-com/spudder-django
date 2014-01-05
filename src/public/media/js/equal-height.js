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

function resizeImagesWithAspectRation ($images, config) {
    // Code from StackOverflow: http://stackoverflow.com/questions/3971841/how-to-resize-images-proportionally-keeping-the-aspect-ratio
    $images.each(function() {
        var ratio = 0;  // Used for aspect ratio
        var width = $(this).width();    // Current image width
        var height = $(this).height();  // Current image height

        // Check if the current width is larger than the max
        if(width > config.maxWidth){
            ratio = config.maxWidth / width;   // get ratio for scaling image
            $(this).css("width", config.maxWidth); // Set new width
            $(this).css("height", height * ratio);  // Scale height based on ratio
            height = height * ratio;    // Reset height to match scaled image
            width = width * ratio;    // Reset width to match scaled image
        }

        // Check if current height is larger than max
        if(height > config.maxHeight){
            ratio = config.maxHeight / height; // get ratio for scaling image
            $(this).css("height", config.maxHeight);   // Set new height
            $(this).css("width", width * ratio);    // Scale width based on ratio
            width = width * ratio;    // Reset width to match scaled image
            height = height * ratio;    // Reset height to match scaled image
        }
    });
}