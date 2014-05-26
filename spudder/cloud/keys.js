module.exports = function () {
    var versions = {
            'spudmart': 0,
            'lukasz': 1,
            'karol': 2
        },
        applicationIds = ['RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR', 'QZjpmUJQEwBE6Wc0YfKEMRwv2C5Aeb4qQbopyIg9', 'YU4g6sCW8Dvl6khJsVYgXhr20Pu5zaaLcIQ4oRON'],
        javascriptKeys = ['zDk1PxddnEJwnLKxrnypGuM4pIq9Z7adAi4rprgH', 'UygLrj7cUKeLSxDWOd7Ch4bEyLfBxQglf2VkGc6Q', 'JRu7BtIEuRDl3QaYNRLguV4a1pFjES02wHfRP5Al'],
        appNames = ['spudmart', 'spudmartlukasz', 'karol'], version = 'spudmart',
        loginWithAmazonClientID = ['amzn1.application-oa2-client.788a2a4986a7412d98417564d8351dc1', 'amzn1.application-oa2-client.46cdd53e23404279b1148162f5f1c0e3', 'amzn1.application-oa2-client.f98d88c846394e5394f6130c0e33941b'],
        baseURLs = ['https://spudmart.parseapp.com', 'https://spudmartlukasz.parseapp.com', 'https://karol.parseapp.com'],
        spudmartURLs = ['https://spudmart1.appspot.com', 'https://lukasz-dot-spudmart1.appspot.com', 'https://karol-dot-spudmart1.appspot.com'];

    try {
        version = require('cloud/private-key.js')();
    } catch (_) {
        // There is no .key.js file which means that main app should be loaded
    }

    return {
        getJavaScriptKey: function () {
            return javascriptKeys[versions[version]];
        },

        getApplicationID: function () {
            return applicationIds[versions[version]];
        },

        getGooglePlacesAPIKey: function () {
            return 'AIzaSyBY2lT_31eUX7yTH90gyPXxcJvM4pqSycs';
        },

        getAppName: function () {
            return appNames[versions[version]];
        },

        getLoginWithAmazonClientID: function () {
            return loginWithAmazonClientID[versions[version]];
        },

        getBaseURL: function () {
            return baseURLs[versions[version]];
        },

        getSpudmartURL: function () {
            return spudmartURLs[versions[version]];
        },

        AWS_ACCESS_KEY_ID: 'AKIAIV6G36242PJ4L7WQ',
        AWS_SECRET_KEY_ID: '5EIFJLrQB6RhtI4wOBLF7DPu4ZyTMbOrwXrneJZg',
        MANDRILL_API_KEY: 'uz2cyx-FdEKZTYLhcKw-OA'
    };
};