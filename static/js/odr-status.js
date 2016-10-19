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

function requestStatus(callback) {
	$('#status > tbody').empty();
	
	$.ajax({
		type: "GET",
		url: "/api/getStatus",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			$.gritter.add({
				title: 'Services status',
				text: "ERROR: " + data['status'] + " : " + data['statusText'],
				image: '/fonts/warning.png',
				sticky: true,
			});
		},
		success: function(data) {
			if ( data['status'] == '0' ) {
				$.each( data['data'], function( key, val ) {
					// 0   - STOPPED
					// 10  - STARTING
					// 20  - RUNNING
					// 30  - BACKOFF
					// 40  - STOPPING
					// 100 - EXITED
					// 200 - FATAL
					// 1000 - UNKNOWN
					
					if ( (val['state'] == '0') || (val['state'] == '40') ) {
						action = '<button type="button" class="btn btn-xs btn-success" id="service_start">Start</button> '
						class_label = 'warning'
					}
					else if ( (val['state'] == '100') || (val['state'] == '200') ) {
						action = '<button type="button" class="btn btn-xs btn-success" id="service_start">Start</button> '
						class_label = 'danger'
					}
					else if ( (val['state'] == '10') || (val['state'] == '20') ) {
						action = '<button type="button" class="btn btn-xs btn-danger" id="service_stop">Stop</button> '
						action = action + '<button type="button" class="btn btn-xs btn-warning" id="service_restart">Restart</button> '
						class_label = 'success'
					}
					else if ( (val['state'] == '30') ) {
						action = '<button type="button" class="btn btn-xs btn-danger" id="service_stop">Stop</button> '
						class_label = 'warning'
					}
					else {
						class_label = 'default'
						action = '<button type="button" class="btn btn-xs btn-success" id="service_start">Start</button> '
						action = action + '<button type="button" class="btn btn-xs btn-danger" id="service_stop">Stop</button> '
						action = action + '<button type="button" class="btn btn-xs btn-warning" id="service_restart">Restart</button> '
					}
					$('#status > tbody:last').append('<tr><td>'+val['name']+'</td><td>'+val['pid']+'</td><td><span class="label label-'+class_label+'">'+val['statename']+'</span></td><td>'+val['description']+'</td><td>'+action+'</td></tr>');

				});
			} else {
				$.gritter.add({
					title: 'Load status',
					text: "ERROR = " + data['status'] + " : " + data['statusText'],
					image: '/fonts/warning.png',
					sticky: true,
				});
			}
		}
	});
}

function requestDLS(callback) {
	$.ajax({
		type: "GET",
		url: "/api/getDLS",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			$('#dls').val("error " + data['status'] + " : " + data['statusText']);
		},
		success: function(data) {
			if (data['dls'] == '') {
				$('#dls').val('No DLS data ...');
			} else {
				$('#dls').val(data['dls']);
			}
		}
	});
	setTimeout(function(){
		requestDLS();},10000);
}

function sleep(delay) {
	var start = new Date().getTime();
	while (new Date().getTime() < start + delay);
}

function serviceAction(action, service) {
	var param = {
		'service': service
	}
	$.ajax({
		type: "POST",
		url: "/api/"+action,
		data: JSON.stringify(param),
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			$.gritter.add({
				title: action+' '+service,
				text: "ERROR : " + data['statusText'].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"),
				image: '/fonts/warning.png',
				sticky: true,
			});
		},
		success: function(data) {
			if (data['status'] != '0') {
				$.gritter.add({
					title: action+' '+service,
					text: "ERROR : " + data['statusText'].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"),
					image: '/fonts/warning.png',
					sticky: true,
				});
			} else {
				$.gritter.add({
					title: action+' '+service,
					image: '/fonts/accept.png',
					text: 'Ok',
				});
			}
		}
	});
}

$(function(){
	requestStatus();
	requestDLS();
	
	$('#refresh').click(function() {
		requestStatus();
		$.gritter.add({
					title: 'Services status refresh',
					image: '/fonts/accept.png',
					text: 'Ok',
				});
	});
	
	$('#status tbody').on( 'click', '#service_start', function () {
		service = $(this).parents('tr').find("td:first").html();
		serviceAction('start', service);
		
		sleep(1000);
		requestStatus();
	});
	
	$('#status tbody').on( 'click', '#service_restart', function () {
		service = $(this).parents('tr').find("td:first").html();
		serviceAction('restart', service);
		
		sleep(1000);
		requestStatus();
	});
	
	$('#status tbody').on( 'click', '#service_stop', function () {
		service = $(this).parents('tr').find("td:first").html();
		serviceAction('stop', service);
		
		sleep(1000);
		requestStatus();
	});
	
	$('#service_stop_all').click(function() {
		var r = confirm("Stop all services. Are you really sure ?");
		if (r == true) {
			$('#status tbody tr').each(function() {
				service = $(this).find("td:first").html();
				serviceAction('stop', service);
			});

			sleep(1000);
			requestStatus();
		}
	});
	
	$('#service_start_all').click(function() {
		var r = confirm("Start all services. Are you really sure ?");
		if (r == true) {
			$('#status tbody tr').each(function() {
				service = $(this).find("td:first").html();
				serviceAction('start', service);
			});
			
			sleep(1000);
			requestStatus();
		}
	});
	
	$('#service_restart_all').click(function() {
		var r = confirm("Restart all services. Are you really sure ?");
		if (r == true) {
			$('#status tbody tr').each(function() {
				service = $(this).find("td:first").html();
				serviceAction('restart', service);
			});
			
			sleep(1000);
			requestStatus();
		}
	});
	
});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});
