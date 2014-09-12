function initializePaginator(totalPages, currentPage, config, handlers) {
    if (!config) {
        config = {};
    }

    if (!handlers) {
        handlers = {};
    }

	if (totalPages > 1) {
        var size = config.size ? config.size : 'small',
            alignment = config.alignment ? config.alignment : 'right';

		var defaultHandlers = {
            pageUrl: function(type, page){
                var currentLocation = window.location.origin + window.location.pathname;
                return currentLocation + "?page=" + page;
            },
            onPageClicked: function (event) {
                event.stopImmediatePropagation();
            }
		};

		$('#paginator').bootstrapPaginator({
		    currentPage: currentPage,
		    totalPages: totalPages,
		    size: size,
	        alignment: alignment,
	        pageUrl: handlers.pageUrl ? handlers.pageUrl : defaultHandlers.pageUrl,
	        onPageClicked: handlers.onPageClicked ? handlers.onPageClicked : defaultHandlers.onPageClicked
	    });
    }
}