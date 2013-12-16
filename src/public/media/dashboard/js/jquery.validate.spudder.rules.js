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
            "positiveInteger",
            function(value) {
                var parsedValue = parseInt(value, 10);

                return !isNaN(parsedValue) && parsedValue > 0;
            },
            "Please enter valid positive integer value."
        );
    });
}(jQuery));