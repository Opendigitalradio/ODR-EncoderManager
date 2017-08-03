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

function requestCards(callback) {
    $("#network_card").empty();
    $.ajax({
        type: "GET",
        url: "/api/getNetworkCards",
        contentType: 'application/json',
        dataType: 'json',
        
        error: function(data) {
            $.gritter.add({
                title: 'Load network cards : ERROR !',
                text: data['status'] + " : " + data['statusText'],
                image: '/fonts/warning.png',
                sticky: true,
            });
        },
        success: function(data) {
            if ( data['status'] == '0' ) {
                var o = new Option('-', '');
                $("#network_card").append(o);
                $.each( data['data'], function( section_key, section_val ) {
                    var o = new Option(section_val['alias'] + ' ('+section_val['card']+')', section_val['card']);
                    $("#network_card").append(o);
                });
            } else {
                $.gritter.add({
                    title: 'Load network cards',
                    text: "ERROR = " + data['status'] + " : " + data['statusText'],
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            }
        }
    });
}

function setEnableDisableDHCP(){
    if ($('#network_dhcp').val() == 'true') {
        $('#network_ip').prop('disabled', true);
        $('#network_mask').prop('disabled', true);
        $('#network_gateway').prop('disabled', true);
    } else {
        $('#network_ip').prop('disabled', false);
        $('#network_mask').prop('disabled', false);
        $('#network_gateway').prop('disabled', false);
    }
}

function requestCardInfo(callback) {
    $.ajax({
        type: "GET",
        url: "/api/getNetworkCards?card="+$('#network_card').val(),
        contentType: 'application/json',
        dataType: 'json',
        
        error: function(data) {
            $.gritter.add({
                title: 'Load network cards : ERROR !',
                text: data['status'] + " : " + data['statusText'],
                image: '/fonts/warning.png',
                sticky: true,
            });
        },
        success: function(data) {
            if ( data['status'] == '0' ) {
                $('#network_ip').val(data['data']['ip']);
                $('#network_mask').val(data['data']['netmask']);
                $('#network_gateway').val(data['data']['gateway']);
                $('#network_dhcp option[value="'+data['data']['dhcp']+'"]').prop('selected', true);
                
                if (data['data']['manage'] == 'true') {
                    $('#network_dhcp').prop('disabled', false);
                    $('#network_ip').prop('disabled', false);
                    $('#network_mask').prop('disabled', false);
                    $('#network_gateway').prop('disabled', false);
                    $('#btn_save').prop('disabled', false);
                    $("#btn_save").removeClass('disabled');
                    setEnableDisableDHCP();
                } else {
                    $('#network_dhcp').prop('disabled', true);
                    $('#network_ip').prop('disabled', true);
                    $('#network_mask').prop('disabled', true);
                    $('#network_gateway').prop('disabled', true);
                    $("#btn_save").addClass('disabled');
                }
                
            } else {
                $.gritter.add({
                    title: 'Load network cards',
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
   requestCards();
   
   $('#network_card').change(function() {
      requestCardInfo();
   });
   
   $('#network_dhcp').change(function() {
      setEnableDisableDHCP();
   });
   
   $('#btn_save').click(function() {
        var param = {
            "card": $('#network_card').val(),
            "ip" : $('#network_ip').val(),
            "netmask" : $('#network_mask').val(),
            "gateway" : $('#network_gateway').val(),
            "dhcp" : $('#network_dhcp').val()
        }
        $.ajax({
            type: "POST",
            url: "/api/setNetworkCard",
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
    });
});
