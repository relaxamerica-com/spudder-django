module.exports = function () {
    return {
        trim: function (text) {
            return text.replace(/^\s+|\s+$/g, '');
        },
        
        fullTrim: function (text) {
        	return text.replace(/(?:(?:^|\n)\s+|\s+(?:$|\n))/g,'').replace(/\s+/g,' ');
        },
        
        removeSpaces: function (text) {
        	return text.replace(/\s+/g, '');
        }
    };
};