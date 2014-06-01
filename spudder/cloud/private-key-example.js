// In order to deploy proper Spudder application different than default one you need to copy this file
// under name private-key.js and change return string to name corresponding with key in keys.js sharedSettings dict.

module.exports = function () {
    return 'spudmart';
};