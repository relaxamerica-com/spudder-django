$(document).ready(function() {
	var datePicker = $('.datePicker'),
		monthSelect = datePicker.find('.month'),
		daySelect = datePicker.find('.day'),
		yearSelect = datePicker.find('.year'),
		MAX = {
			'year' : new Date().getFullYear(),
			'month' : 12,
			'day' : 0
		},
		MIN = {
			'year' : 1920,
			'month' : 1,
			'day' : 1
		},
		defaultDay = 1;
	
	for (var i = MIN['month']; i <= MAX['month']; i++) {
		monthSelect.append(createOption(i));
	}
	
	for (var i = MIN['year']; i <= MAX['year']; i++) {
		var option = createOption(i);
		yearSelect.append(option);
	}
	
	setDefault();
	
	changeDaysInMonthCount();
	
	daySelect.val(defaultDay);
	
	monthSelect.on('change', function() {
		changeDaysInMonthCount();
		
		changeDefualtDate();
	});
	
	yearSelect.on('change', function() {
		changeDaysInMonthCount();
		
		changeDefualtDate();
	});
	
	daySelect.on('change', function() {
		changeDefualtDate();
	});
	
	$('.icon-sort-up').click(function() {
		shiftValue(this, true);
	});
	
	$('.icon-sort-down').click(function() {
		shiftValue(this, false);
	});
	
	function shiftValue(button, isUp) {
		var parent = $(button).parent('.control-group'),
			type = parent.attr('type'),
			select = parent.find('select'),
			value = parseInt(select.val(), 10);

		if (isUp) {
			
			if (value < MAX[type]) {
				select.val(value + 1);
			}
			
		} else {
			
			if (value > MIN[type]) {
				select.val(value - 1);
			}
			
		}
		
		if (type in ['month', 'year']) {
			changeDaysInMonthCount();
		}
		
		changeDefualtDate();
	}
	
	function changeDaysInMonthCount() {
		daySelect.html('');
		
		var year = parseInt(yearSelect.val()),
			month = parseInt(monthSelect.val()) - 1,
			days = calculateDaysInMonth(year, month);
		
		MAX['day'] = days;
		
		for (var i = 1; i <= days; i++) {
			daySelect.append(createOption(i));
		}
		
	}
	
	function createOption(i) {
		var option = $('<option></option');
			
		option.val(i);
		option.html(i);
		return option;
	}
	
	function calculateDaysInMonth(year, month) {
		var monthStart = new Date(year, month, 1),
			monthEnd = new Date(year, month + 1, 1),
			monthLength = (monthEnd - monthStart) / (1000 * 60 * 60 * 24);
		return parseInt(monthLength, 10);
	}
	
	function setDefault() {
		var defaultDate = $('.datePicker').find('.default').val();
		
		if (defaultDate.length) {
			var splitted = defaultDate.split('-');
			
			defaultDay = splitted[0];
			monthSelect.val(splitted[1]);
			yearSelect.val(splitted[2]);
			
		} else {
			yearSelect.val('1980');
		}
	}
	
	function changeDefualtDate() {
		var defaultDateInput = $('.datePicker').find('.default');
		
		defaultDateInput.val([daySelect.val(), monthSelect.val(), yearSelect.val()].join('-'));
	}
});
