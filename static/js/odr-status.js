function requestStatus(callback) {
	$.getJSON( "/api/getStatus", function( data ) {
		$.each( data, function( key, val ) {
			//console.log(key+' '+val['status']);
			if (val['status'] == 'running') {
				$('#status > tbody:last').append('<tr><td>'+key+'</td><td><span class="label label-success">Success</span></td><td>'+val['pid']+'</td></tr>');
			} else {
				$('#status > tbody:last').append('<tr><td>'+key+'</td><td><span class="label label-warning">Warning</span></td><td>'+val['pid']+'</td></tr>');
			}

		});
	});
}

$(function(){
	requestStatus();
	
	$('#refresh').click(function() {
		$('#status > tbody').empty();
		requestStatus();
	});
	
	$('#stop').click(function() {
		var r = confirm("Stop all services. Are you really sure ?");
		if (r == true) {
			$.getJSON( "/api/stop", function( data ) {
				alert(data);
			});
			$('#status > tbody').empty();
			requestStatus();
		}
	});
	
	$('#start').click(function() {
		var r = confirm("Start all services. Are you really sure ?");
		if (r == true) {
			$.getJSON( "/api/start", function( data ) {
				alert(data);
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