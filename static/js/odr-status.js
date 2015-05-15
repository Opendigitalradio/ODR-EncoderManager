function requestStatus(callback) {
	$.ajax({
		type: "GET",
		url: "/api/getStatus",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			alert("error " + data['status'] + " : " + data['statusText']);
		},
		success: function(data) {
			$.each( data, function( key, val ) {
				if (val['status'] == 'running') {
					$('#status > tbody:last').append('<tr><td>'+key+'</td><td><span class="label label-success">Success</span></td><td>'+val['pid']+'</td></tr>');
				} else {
					$('#status > tbody:last').append('<tr><td>'+key+'</td><td><span class="label label-warning">Warning</span></td><td>'+val['pid']+'</td></tr>');
				}

			});
		}
	});
}

function requestDLS(callback) {
	$("#dls").prop('disabled', true);
	$.ajax({
		type: "GET",
		url: "/api/getDLS",
		contentType: 'application/json',
		dataType: 'json',
		
		error: function(data) {
			alert("error " + data['status'] + " : " + data['statusText']);
		},
		success: function(data) {
			$('#dls').val(data['dls']);
		}
	});
	setTimeout(function(){
		requestDLS();},10000);
}

$(function(){
	requestStatus();
	requestDLS();
	
	$('#refresh').click(function() {
		$('#status > tbody').empty();
		requestStatus();
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
					alert("error " + data['status'] + " : " + data['statusText']);
				},
				success: function(data) {
					alert(data);
				}
			});

			$('#status > tbody').empty();
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
					alert("error " + data['status'] + " : " + data['statusText']);
				},
				success: function(data) {
					alert(data);
				}
			});
			
			$('#status > tbody').empty();
			requestStatus();
		}
	});
});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});