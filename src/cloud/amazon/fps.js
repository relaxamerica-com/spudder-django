module.exports = function (keys) {
    return {
        HOST: 'authorize.payments-sandbox.amazon.com',
        PATH: '/cobranded-ui/actions/start',
        PROTOCOL: 'https',
        METHOD: 'GET',

        encodeParams: function (params) {
            var encodedParams = [];

            for (var param in params)
                if (params.hasOwnProperty(param))
                    encodedParams.push(encodeURIComponent(param) + "=" + encodeURIComponent(params[param]));

            return encodedParams.join("&");
        },

        sortParams: function (params) {
            var keys = Object.keys(params),
                i, len = keys.length;

            keys.sort();

            var sortedParams = {};
            for (i = 0; i < len; i++) {
                sortedParams[keys[i]] = params[keys[i]];
            }

            return sortedParams;
        },

        generateSignature: function (params) {
            var sortedParams = this.sortParams(params),
                encodedParams = this.encodeParams(sortedParams),
                string_to_sign = this.METHOD + '\n' + this.HOST + '\n' + this.PATH + '\n' + encodedParams,
                SHAObject = require('cloud/amazon/sha')(string_to_sign, 'TEXT'),
                signature = SHAObject.getHMAC(keys.AWS_SECRET_KEY_ID, 'TEXT', 'SHA-256', 'B64');

            return encodeURIComponent(signature)
        },

        generateGUID: function () {
            function s4() {
                return Math.floor((1 + Math.random()) * 0x10000)
                    .toString(16)
                    .substring(1);
            }

            return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
                    s4() + '-' + s4() + s4() + s4();
        },

        getCBUI: function (params) {
            params.CallerReference = this.generateGUID();
            params.callerKey = keys.AWS_ACCESS_KEY_ID;
            params.SignatureMethod = 'HmacSHA256';
            params.SignatureVersion = 2;

            var encodedParams = this.encodeParams(params),
                signature = this.generateSignature(params);

            return this.PROTOCOL + '://' + this.HOST + this.PATH + '?' + encodedParams +
                    '&Signature=' + signature;
        }
    };
};