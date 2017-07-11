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


// Button handler
$(function(){
	
	$('#btn_backup').click(function() {
    		window.location.href = '/api/backup';
	});


	$('#btn_restore').click(function() {
		var formData = new FormData();
		formData.append('myFile', $('#my-file-selector')[0].files[0]);

		$.ajax({
		        url : '/api/restore',
		        type : 'POST',
		        data : formData,
		        processData: false,  // tell jQuery not to process the data
		        contentType: false,  // tell jQuery not to set contentType

			error: function(data) {
//                        	console.log(data);
	                        $.gritter.add({
	                                title: 'Restore configuration',
	                                text: "ERROR = " + data['status'] + " : " + data['statusText'],
	                                image: '/fonts/warning.png',
	                                sticky: true,
	                        });
        	        },
		       	success : function(data) {
//		        	console.log(data);
//				data = jQuery.parseJSON(data)
	                        if ( data['status'] == '0' ) {
        	                        $.gritter.add({
                	                        title: 'Restore configuration',
                        	                image: '/fonts/accept.png',
                                	        text: 'Ok',
	                                });
        	                } else {
                	                $.gritter.add({
                        	                title: 'Restore configuration',
                                	        text: "ERROR = " + data['status'] + " : " + data['statusText'],
                                        	image: '/fonts/warning.png',
	                                        sticky: true,
        	                        });
                	        }
		        }
		});
        });

});

// ToolTip init
$(function(){
	$('[data-toggle="tooltip"]').tooltip();   
});
