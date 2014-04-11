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
		};
	
	for (var i = MIN['month']; i <= MAX['month']; i++) {
		monthSelect.append(createOption(i));
	}
	
	for (var i = MIN['year']; i <= MAX['year']; i++) {
		var option = createOption(i);
		if (option.val() == '1980') {
			option.attr('selected', 'selected');
		}
		yearSelect.append(option);
	}
	
	changeDaysInMonthCount();
	
	monthSelect.on('change', function() {
		changeDaysInMonthCount();
	});
	
	yearSelect.on('change', function() {
		changeDaysInMonthCount();
	});
	
	$('.icon-sort-up').click(function() {
		shiftValue(this, true);
	});
	
	$('.icon-sort-down').click(function() {
		shiftValue(this, false);
	});
	
	function shiftValue(button, isUp) {
		var select = $(button).parent('.control-group'),
			type = select.attr('type'),
			currentSelected = select.find(':selected'),
			options = select.find('option'),
			index = currentSelected.index();

		if (isUp) {
			
			if (currentSelected.val() < MAX[type]) {
				currentSelected.attr('selected', false);
				$(options.get(index + 1)).attr('selected', 'selected');
			}
			
		} else {
			
			if (currentSelected.val() > MIN[type]) {
				currentSelected.attr('selected', false);
				$(options.get(index - 1)).attr('selected', 'selected');
			}
			
		}
	}
	
	function changeDaysInMonthCount() {
		daySelect.html('');
		
		var year = parseInt(yearSelect.find(':selected').val()),
			month = parseInt(monthSelect.find(':selected').val()) - 1,
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
});
