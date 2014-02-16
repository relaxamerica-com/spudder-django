module.exports = function () {
    return {
        getStatusInfo: function (status) {
            var statusInfo = {
                isError: false,
                errorMessage: ''
            };

            switch (status) {
                case 'A':
                    statusInfo.isError = true;
                    statusInfo.errorMessage = 'Transaction has been aborted by the user.';
                    break;
                case 'CE':
                    statusInfo.isError = true;
                    statusInfo.errorMessage = 'Caller exception';
                    break;
                case 'NP':
                    statusInfo.isError = true;
                    statusInfo.errorMessage = 'Transaction problem';
                    break;
                case 'NM':
                    statusInfo.isError = true;
                    statusInfo.errorMessage = 'You are not registered as a third-party caller to make this transaction. Contact Amazon Payments for more information.';
                    break;
            }

            return statusInfo;
        }
    }

};