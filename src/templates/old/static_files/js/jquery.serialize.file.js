//USAGE: $("#form").serializeFiles();
(function($) {
$.fn.serializeFiles = function() {
    var obj = $(this);
    /* ADD FILE TO PARAM AJAX */
    var formData = new FormData();
    $.each($(obj).find("input[type='file']"), function(i, tag) {
        $.each($(tag)[0].files, function(i, file) {
            formData.append('file-' + i, file); // tag.name
        });
    });
    var params = $(obj).serializeArray();
    $.each(params, function (i, val) {
        formData.append(val.name + '-' + i, val.value);
    });
    return formData;
};
})(jQuery);