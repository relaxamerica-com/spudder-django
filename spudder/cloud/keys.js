module.exports = function () {
    var sharedSettings = {
        'spudmart': {
            applicationId: 'RwjN7ubrqVZSXcwd2AWaQtov6Mgsi7hAXZ510xTR',
            javascriptKey: 'zDk1PxddnEJwnLKxrnypGuM4pIq9Z7adAi4rprgH',
            appName: 'spudmart',
            loginWithAmazonClientID: 'amzn1.application-oa2-client.788a2a4986a7412d98417564d8351dc1',
            baseURL: 'https://spudmart.parseapp.com',
            spudmartURL: 'https://spudmart1.appspot.com'
        },
        'lukasz': {
            applicationId: 'QZjpmUJQEwBE6Wc0YfKEMRwv2C5Aeb4qQbopyIg9',
            javascriptKey: 'UygLrj7cUKeLSxDWOd7Ch4bEyLfBxQglf2VkGc6Q',
            appName: 'spudmartlukasz',
            loginWithAmazonClientID: 'amzn1.application-oa2-client.46cdd53e23404279b1148162f5f1c0e3',
            baseURL: 'https://spudmartlukasz.parseapp.com',
            spudmartURL: 'https://sharp-avatar-587.appspot.com'
        },
        'karol': {
            applicationId: 'YU4g6sCW8Dvl6khJsVYgXhr20Pu5zaaLcIQ4oRON',
            javascriptKey: 'JRu7BtIEuRDl3QaYNRLguV4a1pFjES02wHfRP5Al',
            appName: 'karol',
            loginWithAmazonClientID: 'amzn1.application-oa2-client.f98d88c846394e5394f6130c0e33941b',
            baseURL: 'https://karol.parseapp.com',
            spudmartURL: 'https://essential-hawk-597.appspot.com'
        }
    },
        version = 'spudmart';

    try {
        version = require('cloud/private-key.js')();
    } catch (_) {
        // There is no private-key.key.js file which means that main app should be loaded
    }

    return {
        getJavaScriptKey: function () {
            return sharedSettings[version].javascriptKey;
        },

        getApplicationID: function () {
            return sharedSettings[version].applicationId;
        },

        getGooglePlacesAPIKey: function () {
            return 'AIzaSyBY2lT_31eUX7yTH90gyPXxcJvM4pqSycs';
        },

        getAppName: function () {
            return sharedSettings[version].appName;
        },

        getLoginWithAmazonClientID: function () {
            return sharedSettings[version].loginWithAmazonClientID;
        },

        getBaseURL: function () {
            return sharedSettings[version].baseURL;
        },

        getSpudmartURL: function () {
            return sharedSettings[version].spudmartURL;
        },

        AWS_ACCESS_KEY_ID: 'AKIAIV6G36242PJ4L7WQ',
        AWS_SECRET_KEY_ID: '5EIFJLrQB6RhtI4wOBLF7DPu4ZyTMbOrwXrneJZg',
        MANDRILL_API_KEY: 'uz2cyx-FdEKZTYLhcKw-OA'
    };
};