// 
// Copyright (C) 2015 Yoann QUERET <yoann@queret.net>
// 

// 
// This file is part of ODR-EncoderManager.
// 
// ODR-EncoderManager is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// ODR-EncoderManager is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with ODR-EncoderManager.  If not, see <http://www.gnu.org/licenses/>.
// 

function requestConfiguration(callback) {
	$.ajax({
		type: "GET",
		url: "/api/getConfig",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			//alert("error " + data['status'] + " : " + data['statusText']);
			$.gritter.add({
				title: 'Load configuration : ERROR !',
				text: data['status'] + " : " + data['statusText'],
				image: '/fonts/warning.png',
				sticky: true,
			});
		},
		success: function(data) {
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
		}
	});
}

function setConfiguration(callback) {
	var param = {
		"global" :	{
					"encoder_dabp_path": $('#global_encoder_dabp_path').val(),
					"encoder_dab_path": $('#global_encoder_dab_path').val(),
					"mot_path": $('#global_mot_path').val(),
					"zmq_tmp_file": $('#global_zmq_tmp_file').val(),
				},
		"telnet" :	{
					"bind_ip": $('#telnet_bind_ip').val(),
					"port": $('#telnet_port').val(),
				},
		"rpc" :		{
					"bind_ip": $('#rpc_bind_ip').val(),
					"port": $('#rpc_port').val(),
				},
		"source" :	{
					"type": $('#source_type').val(),
					"url": $('#source_url').val(),
					"device": $('#source_device').val(),
					"driftcomp": $('#source_driftcomp').val(),
				},
		"output" :	{
					"type": $('#output_type').val(),
					"zmq_host": $('#output_zmq_host').val(),
					"zmq_key": $('#output_zmq_key').val(),
					"dabp_bitrate": $('#output_dabp_bitrate').val(),
					"dabp_samplerate": $('#output_dabp_samplerate').val(),
					"dabp_sbr": $('#output_sbr').val(),
					"dabp_ps": $('#output_ps').val(),
					"dabp_afterburner": $('#output_afterburner').val(),
					"dab_bitrate": $('#output_dab_bitrate').val(),
					"dab_samplerate": $('#output_dab_samplerate').val(),
				},
		"mot" :		{
					"enable": $('#mot_enable').val(),
					"pad": $('#mot_pad').val(),
					"pad_fifo_file": $('#mot_pad_fifo_file').val(),
					"dls_fifo_file": $('#mot_dls_fifo_file').val(),
					"slide_directory": $('#mot_slide_directory').val(),
					"slide_sleeping": $('#mot_slide_sleeping').val(),
					"slide_once": $('#mot_slide_once').val(),
					"raw_dls": $('#mot_raw_dls').val(),
				},
	}
	
	$.ajax({
		type: "POST",
		url: "/api/setConfig",
		data: JSON.stringify(param),
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			$.gritter.add({
				title: 'Write changes : ERROR !',
				text: data['status'] + " : " + data['statusText'],
				image: '/fonts/warning.png',
				sticky: true,
			});
		},
		success: function(data) {
			//alert(data);
			$.gritter.add({
				title: 'Write changes : done !',
				image: '/fonts/accept.png',
				text: data,
			});
		}
	});
}

// Button handler
$(function(){
	$('#reload').click(function() {
		requestConfiguration();
	});
	
	$('#save').click(function() {
		setConfiguration();
	});
	
	$('#apply').click(function() {
		$.ajax({
			type: "GET",
			url: "/api/reloadConfig",
			contentType: 'application/json',
			dataType: 'json',
			
			error: function(data) {
				//alert("error " + data['status'] + " : " + data['statusText']);
				$.gritter.add({
					title: 'Load changes : ERROR !',
					text: data['status'] + " : " + data['statusText'],
					image: '/fonts/warning.png',
					sticky: true,
				});
			},
			success: function(data) {
				//alert(data);
				$.gritter.add({
					title: 'Load changes : done !',
					image: '/fonts/accept.png',
					text: data,
				});
			}
		});
	});
	
	$('#restart').click(function() {
		var r = confirm("Restart encoder. Are you really sure ?");
		if (r == true) {
			$.ajax({
				type: "GET",
				url: "/api/restart",
				contentType: 'application/json',
				dataType: 'json',
				
				error: function(data) {
					//alert("error " + data['status'] + " : " + data['statusText']);
					$.gritter.add({
						title: 'Restart : ERROR !',
						text: data['status'] + " : " + data['statusText'],
						image: '/fonts/warning.png',
						sticky: true,
					});
				},
				success: function(data) {
					//alert(data);
					$.gritter.add({
						title: 'Restart : done !',
						image: '/fonts/accept.png',
						text: data,
					});
				}
			});
		}
	});
});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});