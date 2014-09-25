/*
    Note, this should only be used on forms that have a {{ upload_url }} (blobstore uploads) and must be supported
    by code in the view. For an example supporting view, please see spudderspuds.challenges.views.challenge_accept
 */

function show_form_error($form, error) {
    $('.overlay').remove();
    $form.find('.alert-danger').remove();
    $form.find('.form-group:first').parent().prepend(
        '<div class="alert alert-danger">' +
            '<p><b>Sorry, we could not process your upload</b></p>' +
            '<p>' + error + '</p>' +
        '</div>');
}
$(document).ready(function(){
    $('.ajax-form').ajaxForm({
        beforeSerialize: function($form, options){
            var $body = $('body');
            $body.css('position', 'relative');
            $('<div class="overlay"><div class="inner"><p><i class="fa fa-spin fa-spinner"></i> Uploading<p><div class="progress"><div class="progress-bar" style="width:10%"></div></div></div></div>')
                .appendTo($body);
            $('.overlay .inner').css('top', $(window).scrollTop() + 100);
        },
        error: function(event, type, message, $form){
            show_form_error($form, 'Sorry, there was an error processing your upload, please try again or contact <a href="mailto:support@spudder.com">support</a> if the problem continues.')
        },
        success: function(response_text, status_text, xhr, $form) {
            if (response_text[0] != '/') {
                $form.attr('action', response_text.split('|')[0]);
                show_form_error($form, response_text.split('|')[1]);
            }
            else
                window.location = response_text;
        },
        uploadProgress: function(event, position, total, percent_complete) {
            $('.progress-bar').css('width', '' + percent_complete + "%");
        }
    })
})
