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


function requestUser(callback) {
    $("#user-list").empty();
    $.ajax({
        type: "GET",
        url: "/api/getUser",
        contentType: 'application/json',
        dataType: 'json',
        
        error: function(data) {
            $.gritter.add({
                title: 'Load user : ERROR !',
                text: data['status'] + " : " + data['statusText'],
                image: '/fonts/warning.png',
                sticky: true,
            });
        },
        success: function(data) {
            if ( data['status'] == '0' ) {
                $.each( data['data'], function( section_key, section_val ) {
                    $('#user-list').append(
                        $('<li class="list-group-item user_edit">').append(
                            $('<a>').attr('href','#').attr('data-toggle','modal').attr('data-target','#InfoModal').append(
                                $('<span>').attr('class', 'tab').append(section_val['username'])
                    ))); 
                });
                $('.user_edit a').click(function () {
                    $('#InfoModal h4.modal-title').text("Edit user")
                    $('#InfoModal #edit_username').val($(this).text())
                });   
            } else {
                $.gritter.add({
                    title: 'Load user',
                    text: "ERROR = " + data['status'] + " : " + data['statusText'],
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            }
        }
    });
}


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();   
});

// Onload
$(function(){
    requestUser();
    
    $('#btn_user_add_save').click(function() {
        $('#InfoModalAdd h4.modal-title').text("Add user")
        if ( $('#add_username').val().length >= 2 ) {
            if ( $('#add_password').val() == $('#add_password_confirm').val() ) {
                if ( $('#add_password').val().length >= 6 ) {
                    var param = {
                        "username" : $('#add_username').val(),
                        "password" : $('#add_password').val()
                    }
                    $.ajax({
                        type: "POST",
                        url: "/api/addUser",
                        data: JSON.stringify(param),
                        contentType: 'application/json',
                        dataType: 'text',
                        
                        error: function(data) {
                            //console.log(data);
                            $.gritter.add({
                                title: 'Save',
                                text: "ERROR = " + data['status'] + " : " + data['statusText'],
                                image: '/fonts/warning.png',
                                sticky: true,
                            });
                        },
                        success: function(data) {
                            data = jQuery.parseJSON(data)
                            if ( data['status'] == '0' ) {
                                $.gritter.add({
                                    title: 'Save',
                                    image: '/fonts/accept.png',
                                    text: 'Ok',
                                });
                            } else {
                                $.gritter.add({
                                    title: 'Save',
                                    text: "ERROR = " + data['status'] + " : " + data['statusText'],
                                    image: '/fonts/warning.png',
                                    sticky: true,
                                });
                            }
                        }
                    });
                    $('#add_password').val('');
                    $('#add_password_confirm').val('');
                    $('#InfoModalAdd').modal('hide');
                    requestUser();
                } else {
                    $.gritter.add({
                        title: 'Error !',
                        text: 'Password too short',
                        image: '/fonts/warning.png',
                    }); 
                }
            } else {
                $.gritter.add({
                    title: 'Error !',
                    text: 'Password mistmatch',
                    image: '/fonts/warning.png',
                });
                $('#add_password').val('');
                $('#add_password_confirm').val('');
            }
        } else {
            $.gritter.add({
                title: 'Error !',
                text: 'Username too short',
                image: '/fonts/warning.png',
            });
        }
    });
    
    $('#btn_user_edit_save').click(function() {
        if ( $('#edit_password').val() == $('#edit_password_confirm').val() ) {
            if ( $('#edit_password').val().length >= 6 ) {
                var param = {
                    "username" : $('#edit_username').val(),
                    "password" : $('#edit_password').val()
                }
                $.ajax({
                    type: "POST",
                    url: "/api/setPasswd",
                    data: JSON.stringify(param),
                    contentType: 'application/json',
                    dataType: 'text',
                    
                    error: function(data) {
                        //console.log(data);
                        $.gritter.add({
                            title: 'Save',
                            text: "ERROR = " + data['status'] + " : " + data['statusText'],
                            image: '/fonts/warning.png',
                            sticky: true,
                        });
                    },
                    success: function(data) {
                        data = jQuery.parseJSON(data)
                        if ( data['status'] == '0' ) {
                            $.gritter.add({
                                title: 'Save',
                                image: '/fonts/accept.png',
                                text: 'Ok',
                            });
                        } else {
                            $.gritter.add({
                                title: 'Save',
                                text: "ERROR = " + data['status'] + " : " + data['statusText'],
                                image: '/fonts/warning.png',
                                sticky: true,
                            });
                        }
                    }
                });
            } else {
               $.gritter.add({
                title: 'Error !',
                text: 'Password too short',
                image: '/fonts/warning.png',
            }); 
            }
        } else {
            $.gritter.add({
                title: 'Error !',
                text: 'Password mistmatch',
                image: '/fonts/warning.png',
            });
            $('#edit_password').val('');
            $('#edit_password_confirm').val('');
        }
        
    });
    
    $('#btn_user_edit_delete').click(function() {
        console.log($('ul#user-list li').size());

        if ( $('ul#user-list li').size() == 1 ) {
             $.gritter.add({
                title: 'Error !',
                text: 'You must keep at least one user',
                image: '/fonts/warning.png',
            });
        } else {
            var param = {
                    "username" : $('#edit_username').val()
                }
            $.ajax({
                    type: "POST",
                    url: "/api/delUser",
                    data: JSON.stringify(param),
                    contentType: 'application/json',
                    dataType: 'text',
                    
                    error: function(data) {
                        //console.log(data);
                        $.gritter.add({
                            title: 'Delete',
                            text: "ERROR = " + data['status'] + " : " + data['statusText'],
                            image: '/fonts/warning.png',
                            sticky: true,
                        });
                    },
                    success: function(data) {
                        data = jQuery.parseJSON(data)
                        if ( data['status'] == '0' ) {
                            $.gritter.add({
                                title: 'Delete',
                                image: '/fonts/accept.png',
                                text: 'Ok',
                            });
                        } else {
                            $.gritter.add({
                                title: 'Delete',
                                text: "ERROR = " + data['status'] + " : " + data['statusText'],
                                image: '/fonts/warning.png',
                                sticky: true,
                            });
                        }
                    }
                });
                $('#InfoModal').modal('hide');
                requestUser();
        }

    });
});
