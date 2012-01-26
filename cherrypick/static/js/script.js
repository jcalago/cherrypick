/* Author:

*/

(function($) {

	var COMMA = 44;

	function endsWith(str, suffix) {
	    return str.indexOf(suffix, str.length - suffix.length) !== -1;
	}	

	var methods = {
		init : function(options) {
			var settings = $.extend({
		      'location'         : 'top',
		      'background-color' : 'blue'
		    }, options);

		    var words = []

			this.keypress(function(e) {
				keycode = e.which;
				console.log(keycode);

				switch(e.which) {
					case 38: // up
						e.preventDefault();
						//moveSelect(-1);
						break;

					case 40: // down
						e.preventDefault();
						//moveSelect(1);
						break;

					case 44: // comma
						$input = $(this);
						value = $.trim($input.val());
						console.log(this);
						break;

					case 9:  // tab
					case 13: // return
						e.preventDefault();
						break;
				}
			});



			function appendWord(word) {
				
			}
		}
	};

	jQuery.fn.logger = function(method) {
		if ( methods[method] ) {
			return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
		} else if ( typeof method === 'object' || ! method ) {
			return methods.init.apply( this, arguments );
		} else {
			$.error( 'Method ' +  method + ' does not exist on jQuery.tooltip' );
		} 
	};
})(jQuery);

$(document).ready(function() {



	//$('input#logger').logger();

	/*
	$('input#logger').autocomplete({
    	source: ["c++", "java", "php", "coldfusion", "javascript", "asp", "ruby"],
    	autoFocus: true
	});
	*/

	$('input#logger').tagEditor({
		url: '/Tags', 
		param: 'q', 
		method: 'get', 
		suggestChars: 1, 
		suggestDelay: 300, 
		cache: true, 
		ignoreCase: true, 
		maxTags: 0, 
		tagMaxLength: 0
	}).focus();

	/*
	$(window).scroll(function() {
	    $('nav#menu').css('top', $(this).scrollTop() + "px");
	});
	*/
	
	/*
	var client = new Faye.Client('http://192.168.3.77:8888/faye');
	client.disable('callback-polling');

	var subscription = client.subscribe('/apa', function(message) {
		console.log('faya: ' + message + ' ... ' + new Date());
	});
	*/

});


(function($) {
	$.fn.mustache = function(view, partials) {
		return $($.mustache(this.html(), view, partials));
	};

	$.flash = function(level, message) {
		//$('#message').remove();
		//var $message = $('#message_tmpl').tmpl({'level': level, 'message': message}).prependTo('body');
		var $message = $('#message_tmpl').mustache({'level': level, 'message': message}).prependTo('body');
		$message.slideDown(100);
		setTimeout(function() {
			$message.slideUp(400, function() {
				$(this).remove();
			});
		}, 4000);
	}
	
	$.callAPI = function() {
		var method = arguments[0];
		var cmd = arguments[1];
		var params = null;
		var callback = null;
		
		if (arguments.length == 3) {
			callback = arguments[2];
		} else if (arguments.length == 4) {
			params = arguments[2];
			callback = arguments[3];
		}
		
		$.ajax({
			type:		method,
			url:		'/api/'+cmd+'/',
			data:		params,
			dataType:	'json',
			
			beforeSend:	function() {
				console.log('calling api...');
			},
			
			complete:	function() {
				console.log('done with api...');
			},
			
			success:	function(reply) {
				if (reply.level == -1) {
					$.flash('error', reply.data)
				} else {
					callback(reply);
				}
			}
		});
		//$.post('{% url main__update_item %}', post_data
				
		/*
		$.getJSON('/api/'+cmd+'/', params, function(reply) {
			if (reply.level == -1) {
				$.flash('error', reply.data)
			} else {
				callback(reply);
			}
		});
		*/
	};
	
	$.API = {
		updateItem: function(params, callback) {
			$.callAPI('post', 'update_item', params, callback);
		},
		
		readTask: function(id, callback) {
			$.callAPI('get', 'read_task', callback);			
		}
	
	}
})(jQuery);			

