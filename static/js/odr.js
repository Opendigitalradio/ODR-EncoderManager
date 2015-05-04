function requestConfiguration(callback) {
	$.getJSON( "/api/getConfig", function( data ) {
		$.each( data, function( section_key, section_val ) {
			if ( typeof section_val === 'object') {
				$.each( section_val, function( param_key, param_val ) {
					form_key = section_key + '_' + param_key
					
					if ( $('#'+form_key).attr('type') == 'text' ) {
						$('#'+form_key).val(param_val);
					}
					else if ( $('#'+form_key).attr('type') == 'select' ) {
						$('#'+form_key+' option[value="'+param_val+'"]').prop('selected', true);
					}
					else {
						debug = section_key + '_' + param_key + ':' + param_val;
						console.log('Not found in form: '+debug);
					}
				});
				
			}
		});
	});
}


// Button handler

$(function(){
	$('#reload').click(function() {
		requestConfiguration();
	});
	
	$('#save').click(function() {
		alert('save not yet ready');
	});
	
	$('#restart').click(function() {
		$.getJSON( "/api/restart", function( data ) {
			alert(data);
		});
	});
});