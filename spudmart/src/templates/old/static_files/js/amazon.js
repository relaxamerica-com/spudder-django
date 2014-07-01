$(document).ready(function () {
    if (typeof amazon == undefined) return;

    var $logoutBtn = $('#logout-button');

    if ($logoutBtn.length) {
        $logoutBtn.click(function (event) {
            event.preventDefault();
            amazon.Login.logout();
            window.location = $logoutBtn.attr('href');
        });
    }
});