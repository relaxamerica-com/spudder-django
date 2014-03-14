module.exports = function (keys) {
    function handleAmazonConnectError(httpResponse, res) {
        var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Error connecting with Amazon account', 'href' : 'javascript:void(0);' }],
            jsonResponse = JSON.parse(httpResponse.text);

        res.render('dashboard/fan/amazon/connect_error', {
            'breadcrumbs': breadcrumbs,
            'error': jsonResponse.error_description
        });
    }

    function handleConnectError(error, res) {
        var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Error connecting with Amazon account', 'href' : 'javascript:void(0);' }];

        console.log(error);
        res.render('dashboard/fan/amazon/connect_error', {
            'breadcrumbs': breadcrumbs,
            'error': error
        });
    }

    return {
        connect: function (req, res) {
            var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Connect with Amazon account', 'href' : 'javascript:void(0);' }];
            res.render('dashboard/fan/amazon/connect', { 'breadcrumbs' : breadcrumbs });
        },

        connect_complete: function (req, res) {
            var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Connect with Amazon account', 'href' : 'javascript:void(0);' }];

            var query = req.query,
                accessToken = query.access_token,
                error = query.error;

            if (error) {
                handleConnectError(query.error_description + '<br><a href="' + query.error_uri + '">Learn more</a>', res);
            }

            Parse.Cloud.httpRequest({
                url: 'https://api.amazon.com/auth/O2/tokeninfo?access_token=' + encodeURIComponent(accessToken),
                success: function(httpResponse) {
                    var jsonResponse = JSON.parse(httpResponse.text),
                        isVerified = (jsonResponse.aud == keys.getLoginWithAmazonClientID());

                    if (!isVerified) {
                        handleConnectError('Verification failed! Please contact administrators', res, breadcrumbs);
                    }

                    Parse.Cloud.httpRequest({
                        url: 'https://api.amazon.com/user/profile?access_token=' + encodeURIComponent(accessToken),
                        success: function () {
                            var jsonResponse = JSON.parse(httpResponse.text);

                            Parse.User.current().fetch().then(function(user) {
                                user.set("amazonID", jsonResponse.user_id);
                                user.set("amazonAccessToken", accessToken);

                                user.save(null, {
                                    success: function () {
                                        res.redirect('/dashboard/fans/amazon/connected');
                                    },

                                    error: function (team, error) {
                                        console.log(error);
                                    }
                                });
                            });
                        },
                        error: function (httpResponse) {
                            handleAmazonConnectError(httpResponse, res);
                        }
                    })
                },
                error: function(httpResponse) {
                    handleAmazonConnectError(httpResponse, res);
                }
            });
        },

        connected: function (req, res) {
            var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Connection complete', 'href' : 'javascript:void(0);' }];
            res.render('dashboard/fan/amazon/connected', { 'breadcrumbs': breadcrumbs });
        },

        disconnect: {
            get: function (req, res) {
                var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Disconnect Amazon account', 'href' : 'javascript:void(0);' }];
                res.render('dashboard/fan/amazon/disconnect', { 'breadcrumbs' : breadcrumbs });
            },

            post: function (req, res) {
                Parse.User.current().fetch().then(function(user) {
                    user.set("amazonID", '');
                    user.set("amazonAccessToken", '');

                    user.save(null, {
                        success: function () {
                            res.redirect('/dashboard/fans/amazon/disconnected');
                        },

                        error: function (team, error) {
                            console.log(error);
                        }
                    });
                });
            }
        },

        disconnected: function (req, res) {
            var breadcrumbs = [{ 'title' : 'Fans', 'href' : '/dashboard/fans/settings' }, { 'title' : 'Disconnection complete', 'href' : 'javascript:void(0);' }];
            res.render('dashboard/fan/amazon/disconnected', { 'breadcrumbs': breadcrumbs });
        }
    };
};