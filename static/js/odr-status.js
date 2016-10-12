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
	$.ajax({
		type: "GET",
		url: "/api/getStatus",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			//alert("getStatus\nerror " + data['status'] + " : " + data['statusText']);
			$.gritter.add({
				title: 'Services status',
				text: "ERROR: " + data['status'] + " : " + data['statusText'],
				image: '/fonts/warning.png',
				sticky: true,
			});
		},
		success: function(data) {
			$.each( data, function( key, val ) {
				if (val['state'] == '0') {
					$('#status > tbody:last').append('<tr><td>'+val['name']+'</td><td>'+val['pid']+'</td><td><span class="label label-warning">'+val['statename']+'</span></td><td>'+val['description']+'</td></tr>');
				} else {
					$('#status > tbody:last').append('<tr><td>'+val['name']+'</td><td>'+val['pid']+'</td><td><span class="label label-success">'+val['statename']+'</span></td><td>'+val['description']+'</td></tr>');
				}

			});
		}
	});
}

function requestDLS(callback) {
	//$("#dls").prop('disabled', true);
	$.ajax({
		type: "GET",
		url: "/api/getDLS",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			//alert("getDLS\nerror " + data['status'] + " : " + data['statusText']);
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

$(function(){
	requestStatus();
	requestDLS();
	
	$('#refresh').click(function() {
		$('#status > tbody').empty();
		requestStatus();
		$.gritter.add({
					title: 'Services status refresh',
					image: '/fonts/accept.png',
					text: 'Ok',
				});
	});
	
	$('#stop').click(function() {
		var r = confirm("Stop all services. Are you really sure ?");
		if (r == true) {
			$.ajax({
				type: "GET",
				url: "/api/stop",
				contentType: 'application/json',
				dataType: 'json',
				
				error: function(data) {
					//alert("stop\nerror " + data['status'] + " : " + data['statusText']);
					$.gritter.add({
						title: 'Stop services : ERROR !',
						text: data['status'] + " : " + data['statusText'],
						image: '/fonts/warning.png',
						sticky: true,
					});
				},
				success: function(data) {
					//alert(data);
					$.gritter.add({
						title: 'Stop services : done !',
						image: '/fonts/accept.png',
						text: data,
					});
				}
			});

			$('#status > tbody').empty();
			sleep(1000);
			requestStatus();
		}
	});
	
	$('#start').click(function() {
		var r = confirm("Start all services. Are you really sure ?");
		if (r == true) {
			$.ajax({
				type: "GET",
				url: "/api/start",
				contentType: 'application/json',
				dataType: 'json',
				
				error: function(data) {
					//alert("start\nerror " + data['status'] + " : " + data['statusText']);
					$.gritter.add({
						title: 'Start services : ERROR !',
						text: data['status'] + " : " + data['statusText'],
						image: '/fonts/warning.png',
						sticky: true,
					});
				},
				success: function(data) {
					//alert(data);
					$.gritter.add({
						title: 'Start services : done !',
						image: '/fonts/accept.png',
						text: data,
					});
				}
			});
			
			$('#status > tbody').empty();
			sleep(1000);
			requestStatus();
		}
	});
});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});
