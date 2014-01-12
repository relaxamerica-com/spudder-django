$(document).ready(function () {
    $('#mySignin form').submit(function() {
        var loading = $(this).find('.loading');
        loading.css('visibility', 'visible');

        var email = $(this).find('#loginEmail').val(),
            password = $(this).find('#loginPassword').val(),
            returnURL = $(this).find('input[name="returnURL"]').val(),
            self = this;

        var response = $.post('/accounts/login', { 'email' : email, 'password' : password });

        response.done(function() {
            document.location = returnURL ? returnURL : '/dashboard';
        });

        response.fail(function(error) {
            var alert = $(self).find('.alert-error');
            loading.css('visibility', 'hidden');
            alert.removeClass('hidden');
            alert.html(getErrorMessage('login', error.responseText));
        });

    });

    $('#mySignup form').submit(function() {
        var loading = $(this).find('.loading');
        loading.css('visibility', 'visible');

        var email = $(this).find('#registerEmail').val(),
            password1 = $(this).find('#registerPassword1').val(),
            password2 = $(this).find('#registerPassword2').val(),
            self = this;

        var response = $.post('/accounts/register', { 'email' : email, 'password1' : password1, 'password2' : password2 });

        response.done(function() {
            document.location = '/dashboard/fans/basicInfo';
        });

        response.fail(function(error) {
            var alert = $(self).find('.alert-error');
            loading.css('visibility', 'hidden');
            alert.removeClass('hidden');
            alert.html(getErrorMessage('register', error.responseText));
        });

    });

    function getErrorMessage(type, code) {
        var errors = {
            'login' : {
                '0': 'Email and password are required.',
                '101': 'Email and password not recognized.',
                '-1': 'Opps, something went wrong, please try again.'
            },
            'register' : {
                '0': "Email address is required",
                '1': "Password and password confirmation are required",
                '2': "The passwords you entered did not match",
                '-1': 'Opps, something went wrong, please try again.',
                '202': 'Email already taken.'
            }
        };
        return errors[type][code] ? errors[type][code] : 'An unknown error occured. Please try again or contact administrators.';
    }
});