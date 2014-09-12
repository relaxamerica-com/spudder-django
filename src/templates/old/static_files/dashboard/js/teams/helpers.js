$(document).ready(function() {
    $('.file-upload-input').each(function () {
        $(this).ace_file_input({
            no_file:'No File ...',
            btn_choose:'Choose',
            btn_change:'Select',
            droppable: false,
            onchange: null,
            thumbnail: true,
            whitelist: 'gif|png|jpg|jpeg',
            blacklist: 'exe|php'
        });
    });
});