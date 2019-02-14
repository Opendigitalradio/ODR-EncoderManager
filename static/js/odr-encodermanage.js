//
// Copyright (C) 2019 Yoann QUERET <yoann@queret.net>
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

function requestCoder() {
    $('#coder_available').empty();

    $.ajax({
        type: "GET",
        url: "/api/getCoder",
        contentType: 'application/json',
        dataType: 'json',

        error: function(data) {
            $.gritter.add({
                title: 'Load coder : ERROR !',
                text: data['status'] + " : " + data['statusText'],
                image: '/fonts/warning.png',
                sticky: true,
            });
        },
        success: function(data) {
            if (data['status'] == '-401') {
                console.log('Session timeout. Please login again.')
                $.gritter.add({
                    title: 'Session timeout',
                    text: 'Please <a href="/auth/login?from_page='+window.location.pathname+'"> login</a> again',
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            } else
            if ( data['status'] == '0' ) {
                $.each( data['data'], function( section_key, section_val ) {
                    $('#coder_available').append('<div class="form-group"><div class="coder"><label class="control-label col-sm-2" for="coder_name"></label><div class="col-sm-2"><input type="text" class="form-control" id="coder_name" value="'+ section_val['name'] +'" placeholder="Name"><input type="hidden" id="coder_uniq_id" value="'+ section_val['uniq_id'] +'"></div><div class="col-sm-5"><div class="input-group"><input type="text" class="form-control" id="coder_description" value="'+ section_val['description'] +'" placeholder="Description"><span class="input-group-btn"><button class="btn btn-danger" id="btn_coder_del" type="button" onclick="$(this).parent().parent().parent().parent().parent().remove()"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></span></div></div><button class="btn btn-info btn_coder_info" type="button" data-toggle="modal" data-target="#modal"> <span class="glyphicon glyphicon-info-sign"></span></button></div></div>');
                });

                $('.btn_coder_info').click(function () {
                    coder_uniq_id = $(this).parent().find('input#coder_uniq_id').val()
                    coder_name = $(this).parent().find('input#coder_name').val()
                    coder_description = $(this).parent().find('input#coder_description').val()
                    $('#modal .modal-title').html('Informations about encoder : '+coder_name)
                    $('#modal .modal-body').html('<p><b>uniq_id</b> needed to set DLS/DL+ via API for this encoder is :</p><code>'+ coder_uniq_id +'</code>')
                });

            } else {
                $.gritter.add({
                    title: 'Load coder',
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
    requestCoder();

    $('#btn_coder_add').click(function () {
        $('#coder_available').append('<div class="form-group"><div class="coder"><label class="control-label col-sm-2" for="coder_name"></label><div class="col-sm-2"><input type="text" class="form-control" id="coder_name" value="'+ $('#coder_name').val() +'" placeholder="Name"><input type="hidden" id="coder_uniq_id" value=""></div><div class="col-sm-5"><div class="input-group"><input type="text" class="form-control" id="coder_description" value="'+ $('#coder_description').val() +'" placeholder="Description"><span class="input-group-btn"><button class="btn btn-danger" id="btn_coder_del" type="button" onclick="$(this).parent().parent().parent().parent().parent().remove()"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></span></div></div></div></div>');

        $('#coder_name').val('')
        $('#coder_description').val('')
    });

    $('#btn_coder_save').click(function() {
        var param = [];
        $('#coder_available > .form-group > .coder').each(function () {
            var $input = $(this)
            param.push({name: $input.find('#coder_name').val(), description: $input.find('#coder_description').val(), uniq_id: $input.find('#coder_uniq_id').val()});
        });

        $.ajax({
            type: "POST",
            url: "/api/setCoder",
            data: JSON.stringify(param),
            contentType: 'application/json',
            dataType: 'text',

            error: function(data) {
                $.gritter.add({
                    title: 'Save',
                    text: "ERROR = " + data['status'] + " : " + data['statusText'],
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            },
            success: function(data) {
                data = jQuery.parseJSON(data)
                if (data['status'] == '-401') {
                    console.log('Session timeout. Please login again.')
                    $.gritter.add({
                        title: 'Session timeout',
                        text: 'Please <a href="/auth/login?from_page='+window.location.pathname+'"> login</a> again',
                        image: '/fonts/warning.png',
                        sticky: true,
                    });
                } else
                if ( data['status'] == '0' ) {
                    $.gritter.add({
                        title: 'Save',
                        image: '/fonts/accept.png',
                        text: 'Ok',
                    });
                    requestCoder();
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
    });
});

