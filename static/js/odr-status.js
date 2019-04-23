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

function requestDLS(interval) {
    //console.log('request DLS loaded')

    $.ajax({
        type: "GET",
        url: "/api/getDLS",
        contentType: 'application/json',
        dataType: 'json',

        error: function(data) {
                $.gritter.add({
                    title: 'DLS status',
                    text: "ERROR",
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
            if (data['status'] != '0') {
                $.gritter.add({
                    title: 'DLS status',
                    text: "ERROR : " + data['status'] + " : " + data['statusText'].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"),
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            } else {
                // ADD or UPDATE ROW
                $.each( data['data'], function( key, val ) {
                    dlplus=''
                    if (val['dlplus']) {
                        $.each( val['dlplus'], function( key, val ) {
                            if (dlplus != '') {
                                dlplus += ', '
                            }
                            dlplus += key+': '+val
                        });
                    }

                    coder_tr = $('#dls tr:contains('+val['coder_uniq_id']+')')
                    // if UUID not exist in table, insert new row
                    if ( typeof coder_tr[0] === 'undefined') {
                        //console.log('UUID not found')
                        if (val['status'] != '0') {
                            dls = val['statusText'];
                            dlplus = '';
                            cl = 'disabled';
                        } else {
                            dls = val['dls'];
                            cl = '';
                        }
                        $('#dls > tbody:last').append('<tr><td data-toggle="tooltip" data-placement="top" title="'+val['coder_description']+'">'+val['coder_name']+'</td><td class="hidden">'+val['coder_uniq_id']+'</td><td>'+dls+'</td><td>'+dlplus+'</td><td><button type="button" class="btn btn-xs btn-info dls_edit '+cl+'" id="dls_edit" data-toggle="modal" data-target="#modal"><span class="glyphicon glyphicon-pencil"></span> Edit</button></td></tr>');
                    // else (coder exist in table), update
                    } else {
                        //console.log('UUID found, update')
                        coder_tr.find('td:eq(0)').html(val['coder_name']);
                        coder_tr.find('td:eq(0)').prop('title', val['coder_description']);
                        if (val['status'] != '0') {
                            coder_tr.find('td:eq(2)').html(val['statusText']);
                            coder_tr.find('td:eq(3)').html('');
                            coder_tr.find('td:eq(4) #dls_edit').addClass("disabled");
                        } else {
                            coder_tr.find('td:eq(2)').html(val['dls']);
                            coder_tr.find('td:eq(3)').html(dlplus);
                            coder_tr.find('td:eq(4) #dls_edit').removeClass("disabled");
                        }
                    }
                });

                // REMOVE ROW
                $('#dls > tbody  > tr').each(function( r ) {
                    table_coder_uniq_id = $('#dls > tbody').find('tr:eq('+r+')').find('td:eq(1)').html()
                    exist = 0
                    $.each( data['data'], function( key, val ) {
                        if (val['coder_uniq_id'] == table_coder_uniq_id) {
                            exist = 1
                        }
                    });
                    if (exist == 0) {
                        //console.log('Remove coder uniq_id '+table_coder_uniq_id+' row '+r)
                        $('#dls > tbody').find('tr:eq('+r+')').remove();
                    }
                });

                if  (interval > 0) {
                    //console.log('requestDLS interval ' + interval)
                    requestDLSInterval = setTimeout(function() { requestDLS(interval); }, interval);
                }
            }

        }
    });

}

function requestStatus(callback) {

    $.ajax({
        type: "GET",
        url: "/api/getStatus",
        contentType: 'application/json',
        dataType: 'json',

        error: function(jqXHR, data, errorThrown) {
            $.gritter.add({
                title: 'Process status',
                text: "ERROR",
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
                console.log('request status loaded')
                $('#status > tbody').empty();

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
                        action = '<button type="button" class="btn btn-xs btn-success" id="service_start"><span class="glyphicon glyphicon-play"></span> Start</button> '
                        class_label = 'warning'
                    }
                    else if ( (val['state'] == '100') || (val['state'] == '200') ) {
                        action = '<button type="button" class="btn btn-xs btn-success" id="service_start"><span class="glyphicon glyphicon-play"></span> Start</button> '
                        class_label = 'danger'
                    }
                    else if ( (val['state'] == '10') || (val['state'] == '20') ) {
                        action = '<button type="button" class="btn btn-xs btn-danger" id="service_stop"><span class="glyphicon glyphicon-stop"></span> Stop</button> '
                        action = action + '<button type="button" class="btn btn-xs btn-warning" id="service_restart"><span class="glyphicon glyphicon-repeat"></span> Restart</button> '
                        class_label = 'success'
                    }
                    else if ( (val['state'] == '30') ) {
                        action = '<button type="button" class="btn btn-xs btn-danger" id="service_stop"><span class="glyphicon glyphicon-stop"></span> Stop</button> '
                        class_label = 'warning'
                    }
                    else if ( (val['state'] == '1000') ) {
                        class_label = 'default'
                        action = ''
                    }
                    else {
                        class_label = 'default'
                        action = '<button type="button" class="btn btn-xs btn-success" id="service_start"><span class="glyphicon glyphicon-play"></span> Start</button> '
                        action = action + '<button type="button" class="btn btn-xs btn-danger" id="service_stop"><span class="glyphicon glyphicon-stop"></span> Stop</button> '
                        action = action + '<button type="button" class="btn btn-xs btn-warning" id="service_restart"><span class="glyphicon glyphicon-repeat"></span> Restart</button> '
                    }

                    if ( val['coder_name'] == 'Other process' ) {
                        service=val['name']
                    } else {
                        service=val['name'].split('-')[0] + '-' + val['name'].split('-')[1];
                    }

                    $('#status > tbody:last').append('<tr><td data-placement="top" title="'+val['coder_description']+'">'+val['coder_name']+'</td><td class="hidden">'+val['coder_uniq_id']+'</td><td>'+service+'</td><td>'+val['pid']+'</td><td><span class="label label-'+class_label+'">'+val['statename']+'</span></td><td>'+val['description']+'</td><td>'+action+'</td></tr>');

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

function sleep(delay) {
    var start = new Date().getTime();
    while (new Date().getTime() < start + delay);
}

function serviceAction(action, service, uniq_id, coder) {
    console.log(action+' '+service+' '+uniq_id+' '+coder)
    if (uniq_id == '') {
        var param = {
        'service': service
        }
    } else {
        var param = {
            'service': service+'-'+uniq_id
        }
    }
    $.ajax({
        type: "POST",
        url: "/api/"+action,
        data: JSON.stringify(param),
        contentType: 'application/json',
        dataType: 'json',

        error: function(data) {
            $.gritter.add({
                title: action+' '+coder+' '+service,
                text: "ERROR : " + data['statusText'].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"),
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
            if (data['status'] != '0') {
                $.gritter.add({
                    title: action+' '+coder+' '+service,
                    text: "ERROR : " + data['statusText'].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"),
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            } else {
                $.gritter.add({
                    title: action+' '+coder+' '+service,
                    image: '/fonts/accept.png',
                    text: 'Ok',
                });

                sleep(1000);
                requestStatus();
            }
        }
    });
}

function updateDLS(coder_uniq_id, dls) {
    console.log('update DLS for '+coder_uniq_id+' : '+dls)
    var param = {
        'uniq_id': coder_uniq_id,
        'dls': dls,
        'output': 'json'
    }
    $.ajax({
        type: "POST",
        url: "/api/setDLS",
        data: param,

        error: function(data) {
            $.gritter.add({
                title: 'DLS update',
                text: "ERROR : " + data['statusText'],
                image: '/fonts/warning.png',
                sticky: true,
            });
        },
        success: function(data) {
            if (data[0]['status'] != '0') {
                $.gritter.add({
                    title: 'DLS update',
                    text: "ERROR : " + data['statusText'],
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            } else {
                $.gritter.add({
                    title: 'DLS update',
                    image: '/fonts/accept.png',
                    text: 'Ok',
                });
                $('#modal').modal('hide');
            }
        }
    });
}

$(function(){
    requestDLS(1000);
    requestStatus();

    $('#refresh').click(function() {
        requestStatus();
    });

    $('#dls tbody').on( 'click', '#dls_edit', function () {
        coder_name = $(this).parents('tr').find("td:eq(0)").html();
        coder_uniq_id = $(this).parents('tr').find("td:eq(1)").html();
        dls = $(this).parents('tr').find("td:eq(2)").html();

        $('#modal .modal-title').html('Edit '+coder_name)
        $('#modal .modal-body').html('<form><div class="form-group"><label for="dls_content">DLS:</label><input type="hidden" id="edit_dls_coder_uniq_id" value="'+ coder_uniq_id +'"><input type="text" class="form-control" id="edit_dls_content" value="'+ dls +'"></div><button type="button" id="edit_btn_dls" class="btn btn-default">Submit</button></form>')
    });

    $('#modal').on( 'click', '#edit_btn_dls', function () {
        coder_name = $(this).parents('tr').find("td:eq(0)").html();
        coder_uniq_id = $(this).parents('tr').find("td:eq(1)").html();
        dls = $(this).parents('tr').find("td:eq(2)").html();
        updateDLS( $('#edit_dls_coder_uniq_id').val(), $('#edit_dls_content').val() )
    });

    $('#status tbody').on( 'click', '#service_start', function () {
        //service = $(this).parents('tr').find("td:first").html();
        service = $(this).parents('tr').find("td").eq(2).html();
        uniq_id = $(this).parents('tr').find("td").eq(1).html();
        coder = $(this).parents('tr').find("td").eq(0).html();
        serviceAction('start', service, uniq_id, coder);
    });

    $('#status tbody').on( 'click', '#service_restart', function () {
        //service = $(this).parents('tr').find("td:first").html();
        service = $(this).parents('tr').find("td").eq(2).html();
        uniq_id = $(this).parents('tr').find("td").eq(1).html();
        coder = $(this).parents('tr').find("td").eq(0).html();
        serviceAction('restart', service, uniq_id, coder);
    });

    $('#status tbody').on( 'click', '#service_stop', function () {
        //service = $(this).parents('tr').find("td:first").html();
        service = $(this).parents('tr').find("td").eq(2).html();
        uniq_id = $(this).parents('tr').find("td").eq(1).html();
        coder = $(this).parents('tr').find("td").eq(0).html();
        serviceAction('stop', service, uniq_id, coder);
    });

    $('#service_stop_all').click(function() {
        var r = confirm("Stop all services. Are you really sure ?");
        if (r == true) {
            $('#status tbody tr').each(function() {
                //service = $(this).find("td:first").html();
                service = $(this).find("td").eq(2).html();
                uniq_id = $(this).find("td").eq(1).html();
                coder = $(this).find("td").eq(0).html();
                serviceAction('stop', service, uniq_id, coder);
            });
        }
    });

    $('#service_start_all').click(function() {
        var r = confirm("Start all services. Are you really sure ?");
        if (r == true) {
            $('#status tbody tr').each(function() {
                //service = $(this).find("td:first").html();
                service = $(this).find("td").eq(2).html();
                uniq_id = $(this).find("td").eq(1).html();
                coder = $(this).find("td").eq(0).html();
                serviceAction('start', service, uniq_id, coder);
            });
        }
    });

    $('#service_restart_all').click(function() {
        var r = confirm("Restart all services. Are you really sure ?");
        if (r == true) {
            $('#status tbody tr').each(function() {
                //service = $(this).find("td:first").html();
                service = $(this).find("td").eq(2).html();
                uniq_id = $(this).find("td").eq(1).html();
                coder = $(this).find("td").eq(0).html();
                serviceAction('restart', service, uniq_id, coder);
            });
        }
    });

});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();
});
