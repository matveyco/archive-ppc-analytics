timeSpent = 0;
// Вспомогательное
var ajax = {
	/**
	 * Настройка служебной AJAX-фигни
	 */
	setup : function() {
		$.ajaxSetup({
			cache : false,
			crossDomain : false,
			error : ajax.errorhandler,
		});
	},
	/**
	 * Обработчик ошибок AJAX-подгрузки
	 * 
	 * @param XMLHttpRequest
	 *            object Объект XMLHttpRequest
	 * @param ajaxOptions
	 *            string Строка, описывающая тип случившейся ошибки
	 * @param thrownError
	 *            object Объект исключений
	 */
	errorhandler : function(XMLHttpRequest, ajaxOptions, thrownError) {
		console.warn(XMLHttpRequest);
		console.warn(ajaxOptions);
		console.warn(thrownError);
	},
	/**
	 * Простой логгер
	 * 
	 * @param response
	 *            string Строка ответа от AJAX
	 */
	simplelogger : function(response) {
		console.log(response);
	},
	check_cookies : function() {
		var cookieEnabled = (navigator.cookieEnabled) ? true : false;
		if (typeof navigator.cookieEnabled == "undefined" && !cookieEnabled) {
			document.cookie = "testcookie";
			cookieEnabled = (document.cookie.indexOf("testcookie") != -1) ? true : false;
		}
		return cookieEnabled;
	},
	check_autoplay : function() {
		return $('.video-autoplay video')[0].paused;
	},
}
var links_data = {
	0 : {
		'name' : 'Main',
		'icon' : 'icon-user',
		'href' : ''
	},
	1 : {
		'name' : 'Work',
		'icon' : 'icon-briefcase',
		'href' : 'work'
	},
	2 : {
		'name' : 'Resume',
		'icon' : 'icon-list',
		'href' : 'resume'
	},
	3 : {
		'name' : 'Contact',
		'icon' : 'icon-mail',
		'href' : 'contact'
	},
}
// Автоматические процессы
var process = {
	update_js : function(web_id, sub_id, host_id, hit_id) {
		$.ajax({
			url : '/update/js/' + web_id + '/' + sub_id + '/' + host_id + '/' + hit_id + '/',
			type : 'PUT',
			success : ajax.simplelogger,

		});
	},
	update_flash : function(web_id, sub_id, host_id, hit_id) {
		$.ajax({
			url : '/update/flash/' + web_id + '/' + sub_id + '/' + host_id + '/' + hit_id + '/',
			type : 'PUT',
			data : {
				flash_enabled : FlashDetect.installed ? 1 : 0,
				flash_version : FlashDetect.raw,
			},
			success : ajax.simplelogger,
		});
	},
	update_cookies : function(web_id, sub_id, host_id, hit_id) {
		if (ajax.check_cookies()) {
			$.ajax({
				url : '/update/cookies/' + web_id + '/' + sub_id + '/' + host_id + '/' + hit_id + '/',
				type : 'PUT',
				success : ajax.simplelogger,
			});
		}
	},
	update_autoplay : function(web_id, sub_id, host_id, hit_id) {
		if (pages.index.regex.test(window.location.pathname)) {
			if (ajax.check_autoplay()) {
				$.ajax({
					url : '/update/autoplay/' + web_id + '/' + sub_id + '/' + host_id + '/' + hit_id + '/',
					type : 'PUT',
					success : ajax.simplelogger,
				});
			}
		}
	},
	create_links : function(web_id, sub_id, host_id, hit_id) {
		$("ul.nav > li.js-link").each(function(index) {
			var link = links_data[index]['href'].length ? '/' + web_id + '/' + sub_id + '/' + links_data[index]['href'] + '/' : '/' + web_id + '/' + sub_id + '/';
			$(this).html('<a href="' + link + '" class="' + links_data[index]['icon'] + '"><span>' + links_data[index]['name'] + '</span></a>');
		});
	},
}
// Обработчики
var handlers = {
	flash : function(event) {
		$.ajax({
			url : '/click/flash/' + event.data + '/',
			type : 'PUT',
			success : ajax.simplelogger,

		});
	},
	js : function(event) {
		$.ajax({
			url : '/click/js/' + event.data + '/',
			type : 'PUT',
			success : ajax.simplelogger,

		});
	},
	video : function(event) {
		$.ajax({
			url : '/click/video/' + event.data + '/',
			type : 'PUT',
			success : ajax.simplelogger,

		});
	},
	timer : {
		start : function() {
			timer = setInterval(function() {
				timeSpent++;
			}, 998);
		},
		end : function(event) {
			timer = clearInterval(timer);
			$.ajax({
				type : "PUT",
				url : '/update/time/' + event.data[0] + '/' + event.data[1] + '/',
				async : false,
				data : {
					time : timeSpent
				},
				success : ajax.simplelogger,
			});
		},
	},
	inner : function(event) {
		$.ajax({
			url : '/click/inner/' + event.data + '/',
			type : 'PUT',
			success : ajax.simplelogger,

		});
	},
	outer : function(event) {
		$.ajax({
			url : '/click/outer/' + event.data + '/',
			type : 'PUT',
			success : ajax.simplelogger,

		});
	},
	debug : function() {
		console.log('test');
	},
}
// Страницы
var pages = {
	index : {
		regex : new RegExp('^/([0-9]+/(redirect/[0-9]+/)?)?$'),
	},
}
// OnLoad
$(function() {
	var host_id = $('#host_id').text();
	var hit_id = $('#hit_id').text();
	var web_id = $('#web_id').text();
	var sub_id = $('#sub_id').text();
	ajax.setup();

	handlers.timer.start();
	$(window).on('unload', null, [ host_id, hit_id ], handlers.timer.end);

	$('.js-link').on('click', null, hit_id, handlers.js);
	$('.inner-link').on('click', null, hit_id, handlers.inner);
	$('.outer-link').on('click', null, hit_id, handlers.outer);

	for (name in process) {
		process[name](web_id, sub_id, host_id, hit_id);
	}
	// Only main page
	if (pages.index.regex.test(window.location.pathname)) {
		$('embed').removeAttr('style');
		$('#swf_tracker').on('mousedown', null, hit_id, handlers.flash);
		$('video').on('click', null, hit_id, handlers.video);
	}
});
