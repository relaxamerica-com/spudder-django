$(document).ready(function () {
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
                '125': "Email invalid",
                '202': 'Email already taken.'
            }
        };
        return errors[type][code] ? errors[type][code] : 'An unknown error occured. Please try again or contact administrators.';
    }

    window.handleSignInForm = function ($form) {
        $form.submit(function() {
            var $loading = $(this).find('.loading'),
                $alert = $(this).find('.alert');

            $loading.css('visibility', 'visible');
            $alert.removeClass('alert-error').hide();

            var email = $(this).find('input[name="email"]').val(),
                password = $(this).find('input[name="password"]').val(),
                returnURL = $(this).find('input[name="returnURL"]').val();

            var response = $.post('/accounts/login', { 'email' : email, 'password' : password });

            response.always(function(statusCode) {
                if (statusCode == '200') {
                    document.location = returnURL ? returnURL : '/dashboard';
                } else {
                    $loading.css('visibility', 'hidden');
                    $alert.addClass('alert-error').show();
                    $alert.html(getErrorMessage('login', statusCode));
                }
            });
        });
    };

    window.handleSignUpForm = function ($form) {
        $form.submit(function() {
            var $loading = $(this).find('.loading'),
                $alert = $(this).find('.alert');

            $loading.css('visibility', 'visible');
            $alert.removeClass('alert-error').hide();

            var email = $(this).find('input[name="email"]').val(),
                password1 = $(this).find('input[name="password1"]').val(),
                password2 = $(this).find('input[name="password2"]').val(),
                returnURL = $(this).has('input[name="returnURL"]').length ? $(this).find('input[name="returnURL"]').val() : undefined,
                acceptInvitation = $('input[name="acceptInvitation"]');

            var response = $.post('/accounts/register', { 'email' : email, 'password1' : password1, 'password2' : password2 });

            response.always(function(statusCode) {
                if (statusCode == '200') {
                    if (returnURL) {
                        document.location = returnURL;
                    } else {
                        if ( acceptInvitation.val().length > 0 ) {
                            $.get('/acceptEntityInvitation/' + acceptInvitation.val(), function() {
                                document.location = '/dashboard/fans/basicInfo#invitationAccepted';
                            });
                        } else {
                            document.location = '/dashboard/fans/basicInfo';
                        }
                    }
                } else {
                    $loading.css('visibility', 'hidden');
                    $alert.addClass('alert-error').show();
                    $alert.html(getErrorMessage('register', statusCode));
                }
            });

        });
    };

    window.handleSignInForm($('#mySignin').find('form'));
    window.handleSignUpForm($('#mySignup').find('form'));
});