var misc = {

	datepicker : function() {
		$('#dp').datepicker().on(
				'changeDate',
				function(ev) {
					date = new Date(ev.date);
					url = date.getFullYear()
							+ '/' + (date.getMonth()+1) + '/' + date.getDate()
							+ '/';
					$.get(url, function(data) {
						$('#stats tbody').html(data);
					});
					$('#dp').datepicker('hide');
				});
	},
}
$(function() {
	misc.datepicker();
});
