// 
// Copyright (C) 2020 Yoann QUERET <yoann@queret.net>
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
                                dlplus += '<br />'
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
                        $('#dls > tbody:last').append('<tr><td data-toggle="tooltip" data-placement="top" title="'+val['coder_description']+'">'+val['coder_name']+'</td><td class="hidden">'+val['coder_uniq_id']+'</td><td>'+dls+'</td><td>'+dlplus+'</td><td><button type="button" class="btn btn-xs btn-info dls_edit '+cl+'" id="dls_edit" data-toggle="modal" data-target="#modal"><span class="glyphicon glyphicon-pencil"></span> Edit</button> <button type="button" class="btn btn-xs btn-info" id="audio_level" data-toggle="modal" data-target="#modal"><span class="glyphicon glyphicon-stats"></span> Audio levels</button></td></tr>');
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

                    if (val['configuration_changed'] == true) {
                        info = '<div class="text-right"><button type="button" class="btn btn-danger btn-xs" data-toggle="tooltip" data-placement="left" title="The configuration has changed. Restart required."><span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span></button></div>'
                    } else {
                        info = ''
                    }

                    if ( val['coder_name'] == 'Other process' ) {
                        service=val['name']
                    } else {
                        service=val['name'].substring(0, val['name'].length - 37);
                    }

                    $('#status > tbody:last').append('<tr><td data-placement="top" title="'+val['coder_description']+'">'+val['coder_name']+'</td><td class="hidden">'+val['coder_uniq_id']+'</td><td>'+service+'</td><td>'+val['pid']+'</td><td><span class="label label-'+class_label+'">'+val['statename']+'</span></td><td>'+val['description']+'</td><td>'+info+'</td><td>'+action+'</td></tr>');

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
    var param = {
        'service': service,
        'uniq_id': uniq_id,
        'coder': coder
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

function refreshAudioLevel(uniq_id, interval) {
    $.ajax({
        type: "GET",
        url: "/api/getAudioLevel?uniq_id=" + uniq_id,
        contentType: 'application/json',
        dataType: 'json',

        error: function(data) {
            $('#lLevel').html('error');
            $('#rLevel').html('error');
        },
        success: function(data) {

                // CALCULATE VALUE

                    if (data['status'] != 0) {
                        l=0
                        r=0
                        $('#lLevel').html(data['statusText']);
                        $('#rLevel').html(data['statusText']);
                    }
                    else if (data['data']['state'] != 20) {
                        l=0
                        r=0
                        $('#lLevel').html('not running');
                        $('#rLevel').html('not running');
                    }
                    else {
                        l=data['data']['audio']['audio_l']
                        r=data['data']['audio']['audio_r']

                        $('#lLevel').html(l+' dB');
                        $('#rLevel').html(r+' dB');

                        // Bar Graph
                        if (data['data']['audio']['audio_l'] <= -80) { l=0 }
                        if ((data['data']['audio']['audio_l'] > -80) && (data['data']['audio']['audio_l'] <= -40)) { l=1 }
                        if ((data['data']['audio']['audio_l'] > -40) && (data['data']['audio']['audio_l'] <= -30)) { l=2 }
                        if ((data['data']['audio']['audio_l'] > -30) && (data['data']['audio']['audio_l'] <= -20)) { l=3 }
                        if ((data['data']['audio']['audio_l'] > -20) && (data['data']['audio']['audio_l'] <= -12)) { l=4 }
                        if ((data['data']['audio']['audio_l'] > -12) && (data['data']['audio']['audio_l'] <= -11)) { l=5 }
                        if ((data['data']['audio']['audio_l'] > -11) && (data['data']['audio']['audio_l'] <= -10)) { l=6 }
                        if ((data['data']['audio']['audio_l'] > -10) && (data['data']['audio']['audio_l'] <= -9)) { l=7 }
                        if ((data['data']['audio']['audio_l'] > -9) && (data['data']['audio']['audio_l'] <= -8)) { l=8 }
                        if ((data['data']['audio']['audio_l'] > -8) && (data['data']['audio']['audio_l'] <= -7)) { l=9 }
                        if ((data['data']['audio']['audio_l'] > -7) && (data['data']['audio']['audio_l'] <= -6)) { l=10 }
                        if ((data['data']['audio']['audio_l'] > -6) && (data['data']['audio']['audio_l'] <= -5)) { l=11 }
                        if ((data['data']['audio']['audio_l'] > -5) && (data['data']['audio']['audio_l'] <= -4)) { l=12 }
                        if ((data['data']['audio']['audio_l'] > -4) && (data['data']['audio']['audio_l'] <= -3)) { l=13 }
                        if ((data['data']['audio']['audio_l'] > -3) && (data['data']['audio']['audio_l'] <= -2)) { l=14 }
                        if ((data['data']['audio']['audio_l'] > -2) && (data['data']['audio']['audio_l'] <= -1)) { l=15 }
                        if (data['data']['audio']['audio_l'] > -1) { l=16 }

                        if (data['data']['audio']['audio_r'] <= -80) { r=0 }
                        if ((data['data']['audio']['audio_r'] > -80) && (data['data']['audio']['audio_r'] <= -40)) { r=1 }
                        if ((data['data']['audio']['audio_r'] > -40) && (data['data']['audio']['audio_r'] <= -30)) { r=2 }
                        if ((data['data']['audio']['audio_r'] > -30) && (data['data']['audio']['audio_r'] <= -20)) { r=3 }
                        if ((data['data']['audio']['audio_r'] > -20) && (data['data']['audio']['audio_r'] <= -12)) { r=4 }
                        if ((data['data']['audio']['audio_r'] > -12) && (data['data']['audio']['audio_r'] <= -11)) { r=5 }
                        if ((data['data']['audio']['audio_r'] > -11) && (data['data']['audio']['audio_r'] <= -10)) { r=6 }
                        if ((data['data']['audio']['audio_r'] > -10) && (data['data']['audio']['audio_r'] <= -9)) { r=7 }
                        if ((data['data']['audio']['audio_r'] > -9) && (data['data']['audio']['audio_r'] <= -8)) { r=8 }
                        if ((data['data']['audio']['audio_r'] > -8) && (data['data']['audio']['audio_r'] <= -7)) { r=9 }
                        if ((data['data']['audio']['audio_r'] > -7) && (data['data']['audio']['audio_r'] <= -6)) { r=10 }
                        if ((data['data']['audio']['audio_l'] > -6) && (data['data']['audio']['audio_r'] <= -5)) { r=11 }
                        if ((data['data']['audio']['audio_r'] > -5) && (data['data']['audio']['audio_r'] <= -4)) { r=12 }
                        if ((data['data']['audio']['audio_r'] > -4) && (data['data']['audio']['audio_r'] <= -3)) { r=13 }
                        if ((data['data']['audio']['audio_r'] > -3) && (data['data']['audio']['audio_r'] <= -2)) { r=14 }
                        if ((data['data']['audio']['audio_r'] > -2) && (data['data']['audio']['audio_r'] <= -1)) { r=15 }
                        if (data['data']['audio']['audio_r'] > -1) { r=16 }
                    }

                // AUDIO LEVEL DISPLAY
                for (var iter = 1; iter <= 16; iter++) {
                    if (iter <= l) {
                        if (iter == 15) { $( "#l"+iter ).addClass( "led-y-on" ); }
                        else if (iter == 16) { $( "#l"+iter ).addClass( "led-r-on" ); }
                        else { $( "#l"+iter ).addClass( "led-g-on" );}
                    }
                    if (iter > l) {
                        if (iter == 15) { $( "#l"+iter ).removeClass( "led-y-on" ); }
                        else if (iter == 16) { $( "#l"+iter ).removeClass( "led-r-on" ); }
                        else { $( "#l"+iter ).removeClass( "led-g-on" ); }
                    }
                }

                for (var iter = 1; iter <= 16; iter++) {
                    if (iter <= r) {
                        if (iter == 15) { $( "#r"+iter ).addClass( "led-y-on" ); }
                        else if (iter == 16) { $( "#r"+iter ).addClass( "led-r-on" ); }
                        else { $( "#r"+iter ).addClass( "led-g-on" );}
                    }
                    if (iter > r) {
                        if (iter == 15) { $( "#r"+iter ).removeClass( "led-y-on" ); }
                        else if (iter == 16) { $( "#r"+iter ).removeClass( "led-r-on" ); }
                        else { $( "#r"+iter ).removeClass( "led-g-on" ); }
                    }
                }

        }
    });

    if  (interval > 0) {
        console.log('refreshAudioLevel interval ' + interval)
        refreshAudioLevelInterval = setTimeout(function() { refreshAudioLevel(uniq_id, interval); }, interval);
    }
};

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

        $('#modal .modal-title').html('Edit metadatas : '+coder_name)
        $('#modal .modal-body').html('<form><div class="form-group"><label for="dls_content">DLS:</label><input type="hidden" id="edit_dls_coder_uniq_id" value="'+ coder_uniq_id +'"><input type="text" class="form-control" id="edit_dls_content" value="'+ dls +'"></div><button type="button" id="edit_btn_dls" class="btn btn-default">Submit</button></form>')
    });

    $('#dls tbody').on( 'click', '#audio_level', function () {
        coder_name = $(this).parents('tr').find("td:eq(0)").html();
        coder_uniq_id = $(this).parents('tr').find("td:eq(1)").html();
        dls = $(this).parents('tr').find("td:eq(2)").html();

        $('#modal .modal-title').html('Audio levels : '+coder_name)
        $('#modal .modal-body').html('')
        const html_graph = `<div class="panel panel-primary">
            <div class="panel-heading">Audio levels</div>
            <div class="panel-body">
                    <div class="ui-bar" style="font-weight:normal;text-shadow:none;text-align:center">
                    <div style="position:absolute;left:0">L</div>
                    <div class="led-meter led-g-off" id="l1">-40</div>
                    <div class="led-meter led-g-off" id="l2">-30</div>
                    <div class="led-meter led-g-off" id="l3">-20</div>
                    <div class="led-meter led-g-off" id="l4">-12</div>
                    <div class="led-meter led-g-off" id="l5">-11</div>
                    <div class="led-meter led-g-off" id="l6">-10</div>
                    <div class="led-meter led-g-off" id="l7">-9</div>
                    <div class="led-meter led-g-off" id="l8">-8</div>
                    <div class="led-meter led-g-off" id="l9">-7</div>
                    <div class="led-meter led-g-off" id="l10">-6</div>
                    <div class="led-meter led-g-off" id="l11">-5</div>
                    <div class="led-meter led-g-off" id="l12">-4</div>
                    <div class="led-meter led-g-off" id="l13">-3</div>
                    <div class="led-meter led-g-off" id="l14">-2</div>
                    <div class="led-meter led-y-off" id="l15">-1</div>
                    <div class="led-meter led-r-off" id="l16">0</div>
                    <div style="position:absolute;right:0" id="lLevel"></div>
                </div>
                <div class="ui-bar" style="font-weight:normal;text-shadow:none;text-align:center">
                    <div style="position:absolute;left:0">R</div>
                    <div class="led-meter led-g-off" id="r1">-40</div>
                    <div class="led-meter led-g-off" id="r2">-30</div>
                    <div class="led-meter led-g-off" id="r3">-20</div>
                    <div class="led-meter led-g-off" id="r4">-12</div>
                    <div class="led-meter led-g-off" id="r5">-11</div>
                    <div class="led-meter led-g-off" id="r6">-10</div>
                    <div class="led-meter led-g-off" id="r7">-9</div>
                    <div class="led-meter led-g-off" id="r8">-8</div>
                    <div class="led-meter led-g-off" id="r9">-7</div>
                    <div class="led-meter led-g-off" id="r10">-6</div>
                    <div class="led-meter led-g-off" id="r11">-5</div>
                    <div class="led-meter led-g-off" id="r12">-4</div>
                    <div class="led-meter led-g-off" id="r13">-3</div>
                    <div class="led-meter led-g-off" id="r14">-2</div>
                    <div class="led-meter led-y-off" id="r15">-1</div>
                    <div class="led-meter led-r-off" id="r16">0</div>
                    <div style="position:absolute;right:0" id="rLevel"></div>
                </div>
                <div class="ui-bar-legend" style="font-weight:normal;text-shadow:none;text-align:center">
                    <div class="led-legend">-40</div>
                    <div class="led-legend">-30</div>
                    <div class="led-legend">-20</div>
                    <div class="led-legend">-12</div>
                    <div class="led-legend">-11</div>
                    <div class="led-legend">-10</div>
                    <div class="led-legend">-9</div>
                    <div class="led-legend">-8</div>
                    <div class="led-legend">-7</div>
                    <div class="led-legend">-6</div>
                    <div class="led-legend">-5</div>
                    <div class="led-legend">-4</div>
                    <div class="led-legend">-3</div>
                    <div class="led-legend">-2</div>
                    <div class="led-legend">-1</div>
                    <div class="led-legend">0</div>
                    <div class="led-legend">dB</div>
                </div>
            </div>
        </div>`
        $('#modal .modal-body').html(html_graph)
        refreshAudioLevel(coder_uniq_id, 400);
    });

    // Modal - close
    $('#modal').on('hidden.bs.modal', function () {
        if( typeof refreshAudioLevelInterval === 'undefined' || refreshAudioLevelInterval === null ){

        } else {
            clearInterval(refreshAudioLevelInterval);
        }
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
