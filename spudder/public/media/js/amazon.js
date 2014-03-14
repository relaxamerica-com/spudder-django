var loginWithAmazon = document.getElementById('LoginWithAmazon'),
    registerWithAmazon = document.getElementById('RegisterWithAmazon');

if (loginWithAmazon) {
    loginWithAmazon.onclick = function() {
        options = { scope : 'profile' };
        amazon.Login.authorize(options, '<%= baseURL %>/accounts/amazon_login');
        return false;
    };
}

if (registerWithAmazon) {
    registerWithAmazon.onclick = function() {
        options = { scope : 'profile' };
        amazon.Login.authorize(options, '<%= baseURL %>/accounts/amazon_register');
        return false;
    };
}
