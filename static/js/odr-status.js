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
});


// ToolTip init
$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});