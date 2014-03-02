(function($) {
    $(document).ready(function () {
        $.validator.addMethod(
            "endDate",
            function(value) {
                var currentDate = new Date(),
                    currentDay = currentDate.getDate(),
                    currentMonth = currentDate.getMonth() + 1,
                    currentYear = currentDate.getFullYear(),
                    splittedValue = value.split('-'),
                    year = parseInt(splittedValue[0], 10),
                    month = parseInt(splittedValue[1], 10),
                    day = parseInt(splittedValue[2], 10);

                if (currentYear > year) return false;
                if (currentMonth > month) return false;

                return currentDay <= day;
            },
            "End date has to be today or further."
        );

        $.validator.addMethod(
            "originalDate",
            function(value, element) {
                var originalDate = $(element).data('original-end-date').split('-'),
                    originalYear = parseInt(originalDate[0], 10),
                    originalMonth = parseInt(originalDate[1], 10),
                    originalDay = parseInt(originalDate[2], 10),
                    splittedValue = value.split('-'),
                    year = parseInt(splittedValue[0], 10),
                    month = parseInt(splittedValue[1], 10),
                    day = parseInt(splittedValue[2], 10);

                if (originalYear > year) return false;
                if (originalMonth > month) return false;

                return originalDay <= day;
            },
            "End date cannot be set before originally submitted."
        );

        $.validator.addMethod(
            "positiveInteger",
            function(value) {
                var parsedValue = parseInt(value, 10);

                return !isNaN(parsedValue) && parsedValue > 0;
            },
            "Please enter valid positive integer value."
        );
        
        var template = jQuery.validator.format("{0} do NOT exists in our database."),
          _notExistsEmails = '';

        $.validator.addMethod("checkEmailsExists", function(value, element) {
            var notExistsEmails = checkEmailsExists( $('#admins').val() );

            if (notExistsEmails.length == 0) {
                return true;
            } else {
                _notExistsEmails = notExistsEmails.join(', ');
                return false;
            }
        }, function(params, element) {
            return template(_notExistsEmails);
        });

        // jQuery validation custom rules from Stackoverflow
        // URL: http://stackoverflow.com/questions/15794913/jquery-validation-plugin-accept-only-us-canada-and-mexic-zip-code/15795150#15795150
        // ziprange and zipcodeUS are combained into one rule for simplicity
        jQuery.validator.addMethod("zipcodeUS", function(value, element) {
            var isValidRange = this.optional(element) || /^90[2-5]\d\{2\}-\d{4}$/.test(value),
                isValidCode = this.optional(element) || /\d{5}-\d{4}$|^\d{5}$/.test(value);

            return isValidRange && isValidCode;
        }, "The specified US ZIP Code is invalid");
    });
}(jQuery));