$(document).ready(function () {
    var location = window.location,
        returnURL = location.pathname + encodeURIComponent('#') + location.hash.substring(1);

    $("[id^='donation-modal-'] .modal-footer a.accounts-btn").each(function () {
        var currentHref = $(this).attr('href');

        $(this).attr('href', currentHref + '?returnURL=' + returnURL);
    });

    if (location.hash) {
        $(location.hash).modal('show');
    }
});