(function($){

    /* STATIC METHODS *************************************************************************************************/
    $.spudder_challenge_page = {};

    // Init the challenge_page around the page body
    $.spudder_challenge_page.init = function(options) {
        $('body').spudder_challenge_page(options);
    };

    // Show the overlay
    $.spudder_challenge_page.show_overlay = function(options){
        var $el = options.element;
        var message = options.message || 'Loading';
        $el.css('position', 'relative');
        $('.overlay').remove();
        $el.append('' +
                '<div class="overlay">' +
                    '<div class="inner">' +
                        '<p>' +
                            '<i class="fa fa-spin fa-spinner"></i> <span id="uploading-message">' + message + '</span>' +
                        '<p>' +
                    '</div>' +
                '</div>');
    };


    /* INSTANCE METHODS ***********************************************************************************************/
    var methods = {

        // Init and setup function for the challenge page
        init: function(options) {

            // Get a handle on the container
            var $container = this;

            //Attach highlevel event handlers
            $container.spudder_challenge_page('attach_event_handlers');

            var challenge_participation = options.challenge_participation;
            var challenge_root_url = options.root_challenge_url;
            $container.data('challenge_participation', challenge_participation);
            $container.data('current_role', options.current_role);
            $container.data('root_challenge_url', challenge_root_url);

            if (challenge_participation != null && challenge_participation.state_engine != null) {
                $('.action-col > button').attr('disabled', 'disabled');

                var state_engine = challenge_participation.state_engine;
                var $action_container = $('#' + state_engine);
                var $action_col = $action_container.parent();
                $action_col.find(' > button:first').click();
                $action_container.load(challenge_root_url + '/' + challenge_participation.state_engine + '/' + challenge_participation.state_engine_state)
            }

            // Return the container
            return $container;
        },
        attach_event_handlers: function() {
            // Get a handle on the container
            var $container = this;

            $container.find('.action-col > button').click(function(e){
                e.preventDefault();
                e.stopPropagation();
                var $button = $(this);
                var $action_container = $button.parent().find('.action-container:first');
                $action_container.toggleClass('in');
                $container.find('.action-container').each(function(i, el){
                    var $el = $(el);
                    if (!$el.is($action_container))
                        $el.removeClass('in');
                });
                $container.find('.action-col > button').each(function(i, el){
                    var $el = $(el);
                    if (!$el.is($button))
                        $el.removeClass('btn-primary').addClass('btn-default');
                    else
                        $el.removeClass('btn-default').addClass('btn-primary');
                });
            });

            $container.find('.btn-ajax').livequery(function(){
                var $btn = $(this);
                if ($btn.is('button[type=submit]')){
                    $btn.parents('form:first').ajaxForm({
                        beforeSerialize: function ($form, options) {
                            var $btn = $form.find('.btn-ajax');
                            $btn.attr('disabled', 'disabled');
                            $btn.html('<i class="fa fa-spin fa-spinner"></i> ' + $btn.html());
                        },
                        error: function (event, type, message, $form) {
                            alert('Sorry, there was an error processing your upload, please try again or contact support@spudder.com if the problem continues.')
                        },
                        success: function (response_text, status_text, xhr, $form) {
                            var $btn = $form.find('.btn-ajax');
                            var $target = $btn.parents('.action-container:first');
                            $target.html(response_text);
                            if ($(window).scrollTop() > 20)
                                $(window).scrollTop($target.offset().top - 100);
                        }
                    })
                }
                else {
                    $btn.unbind('click').on('click', function(e){
                        e.preventDefault();
                        e.stopPropagation();
                        var $btn = $(this);
                        var $target = $btn.parents('.action-container:first');
                        $btn.attr('disabled', 'disabled');
                        $btn.html('<i class="fa fa-spin fa-spinner"></i> ' + $btn.html());
                        $target.load($btn.attr('href'), function(){
                            if ($(window).scrollTop() > 20)
                                $(window).scrollTop($target.offset().top - 60);
                        });
                    });

                }
            });

            setInterval(function(){
                // find the amount of "seconds" between now and target
                var current_date = new Date().getTime();
                $('.countdown').each(function(i, el){
                    var $countdown = $(el);
                    var target_date = new Date($countdown.data('countdown'));
                    target_date.setDate(target_date.getDate() + 2);
                    var seconds_left = (target_date - current_date) / 1000;
                    var message = "<b>taken too long!</b> But don't worry, you can still click 'Im ready' below";
                    if (seconds_left > 0) {
                        // do some time calculations
                        var days = parseInt(seconds_left / 86400);
                        seconds_left = seconds_left % 86400;

                        var hours = parseInt(seconds_left / 3600);
                        seconds_left = seconds_left % 3600;

                        var minutes = parseInt(seconds_left / 60);
                        var seconds = parseInt(seconds_left % 60);

                        // format countdown string + set tag value
                        message = days + " day" + ((days > 1) ? 's' : '') + ", " + hours + " hours, "
                                + minutes + " minutes and " + seconds + " seconds";
                    }
                    $countdown.html(message);
                })
            }, 1000);

//            $container.find('.btn-state-change').livequery(function(){
//                $(this).unbind('click').on('click', function(e){
//                    e.preventDefault();
//                    e.stopPropagation();
//                    $container.spudder_challenge_page('change_state', $(this));
//                });
//            });
//
            // Return the container
            return $container;
        }
//        ,
//        change_state: function($button) {
//            var $action_container = $button.parents('.action_container:first');
//            $.spudder_challenge_page.show_overlay({element: $action_container});
//            var states = $.spudder_challenge_page.states[$action_container.attr('id')];
//            var current_state_index = $action_container.data('current_state_index') || -1;
//            var next_state_index = current_state_index + 1;
//            var next_state = states[next_state_index];
//            $action_container.load(next_state.url);
//        },
//        load_signin: function(){
//            // Get a handle on the container
//            var $container = this;
//
//            var $action_container = $container.find('.action-container.in');
//
//            $.spudder_challenge_page.show_overlay({element: $action_container});
//
//            // Return the container
//            return $container;
//        }
    };


    /* CONSTRUCTOR ****************************************************************************************************/
    $.fn.spudder_challenge_page = function( method ) {
        if ( methods[method] ) return methods[ method ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        else if ( typeof method === 'object' || ! method ) return methods.init.apply( this, arguments );
        else $.error( 'Method ' +  method + ' does not exist on jQuery.spudder_challenge_page' );
    }
})( jQuery );