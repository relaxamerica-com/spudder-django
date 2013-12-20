module.exports = function () {
    return {
        revertDate: function (originalDate) {
            var splittedDate = originalDate.split('-');

            return splittedDate[2] + '-' + splittedDate[1] + '-' + splittedDate[0];
        }
    };
};