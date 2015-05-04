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

function setConfiguration(callback) {
	var param = {
		"global" :	{	"encoder_path": $('#global_encoder_path').val(),
						"mot_path": $('#global_mot_path').val(),
					},
		"telnet" :	{	"bind_ip": $('#telnet_bind_ip').val(),
						"port": $('#telnet_port').val(),
					},
		"rpc" :		{	"bind_ip": $('#rpc_bind_ip').val(),
						"port": $('#rpc_port').val(),
					},
		"source" :	{	"type": $('#source_type').val(),
						"url": $('#source_url').val(),
						"device": $('#source_device').val(),
						"driftcomp": $('#source_driftcomp').val(),
					},
		"output" :	{	"host": $('#output_host').val(),
						"port": $('#output_port').val(),
						"key_file": $('#output_key_file').val(),
						"bitrate": $('#output_bitrate').val(),
						"samplerate": $('#output_samplerate').val(),
						"sbr": $('#output_sbr').val(),
						"ps": $('#output_ps').val(),
						"afterburner": $('#output_afterburner').val(),
					},
		"mot" :		{	"enable": $('#mot_enable').val(),
						"pad": $('#mot_pad').val(),
						"pad_fifo_file": $('#mot_pad_fifo_file').val(),
						"dls_fifo_file": $('#mot_dls_fifo_file').val(),
						"slide_directory": $('#mot_slide_directory').val(),
						"slide_sleeping": $('#mot_slide_sleeping').val(),
						"slide_once": $('#mot_slide_once').val(),
					},
	}
	console.log(param);
}

// Button handler
$(function(){
	$('#reload').click(function() {
		requestConfiguration();
	});
	
	$('#save').click(function() {
		setConfiguration();
	});
	
	$('#restart').click(function() {
		var r = confirm("Restart encoder. Are you really sure ?");
		if (r == true) {
			$.getJSON( "/api/restart", function( data ) {
				alert(data);
			});
		}
	});
});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});