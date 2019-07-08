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
                if ( data['data'].length == 0) {
                    console.log('00000000000000')
                    $('.page-header').append( 'No encoder configured. Go to <a href="/encodermanage">Encoder > Manage</a> to add one.' );
                }
                $('#tab_coder li').remove();
                $.each(data['data'], function (key, val) {
                    $('<li><p class="coder_uniq_id hidden">'+val['uniq_id']+'</p><a href="#coder" data-toggle="tab">'+val['name']+'</a></li>').appendTo('#tab_coder');
                });
                $('#tab_coder a:first').tab('show');

                // Handler when tab focus change
                $('#tab_coder').on('shown.bs.tab', 'a[data-toggle="tab"]', function (e) {
                    requestConfiguration();
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


function requestConfiguration(reload=false) {
    coder_uniq_id = $('#tab_coder li.active p.coder_uniq_id').tab('show').html()

    console.log('Configuration request for: '+coder_uniq_id)

    $.ajax({
        type: "GET",
        url: "/api/getConfig?uniq_id="+coder_uniq_id,
        contentType: 'application/json',
        dataType: 'json',

        error: function(data) {
            $.gritter.add({
                title: 'Load configuration : ERROR !',
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
                // Set default value
                $('#source_type option[value="stream"]').prop('selected', true);
                $('#source_driftcomp option[value="true"]').prop('selected', true);
                $('#source_silence_detect option[value="true"]').prop('selected', true);
                $('#source_silence_duration').val('60');
                $('#source_alsa_device').val('plughw:1,0');
                $('#source_stream_url').val('');
                $('#source_stream_writeicytext option[value="true"]').prop('selected', true);
                $('#source_avt_input_uri').val('udp://:32010');
                $('#source_avt_control_uri').val('udp://192.168.128.111:9325');
                $('#source_avt_pad_port').val('9405');
                $('#source_avt_jitter_size').val('80');
                $('#source_avt_timeout').val('2000');
                $('#source_aes67_sdp_file').val('/var/tmp/'+coder_uniq_id+'.sdp');
                $('#source_aes67_sdp').text('');
                $('#source_stats_socket').val('/var/tmp/'+coder_uniq_id+'.stats');

                $('#output_type').val('dabp');
                $('#output_bitrate').val('88');
                $('#output_channels option[value="2"]').prop('selected', true);
                $('#output_samplerate option[value="48000"]').prop('selected', true);
                $('#output_dabp_sbr option[value="true"]').prop('selected', true);
                $('#output_dabp_afterburner option[value="true"]').prop('selected', true);
                $('#output_dabp_ps option[value="false"]').prop('selected', true);
                $('#output_dab_dabmode option[value="j"]').prop('selected', true);
                $('#output_dab_dabpsy option[value="1"]').prop('selected', true);
                $('#output_zmq_output').html('');
                $('#output_zmq_key').val('');

                $('#padenc_enable option[value="true"]').prop('selected', true);
                $('#padenc_slide_sleeping').val('0');
                $('#padenc_slide_directory').val('/var/tmp/slide-'+coder_uniq_id+'/');
                $('#padenc_pad_fifo').val('/var/tmp/metadata-'+coder_uniq_id+'.pad');
                $('#padenc_dls_file').val('/var/tmp/metadata-'+coder_uniq_id+'.dls');
                $('#padenc_pad').val('34');
                $('#padenc_slide_once option[value="true"]').prop('selected', true);
                $('#padenc_raw_dls option[value="false"]').prop('selected', true);
                $('#padenc_uniform option[value="true"]').prop('selected', true);
                $('#padenc_uniform_init_burst').val('12');
                $('#padenc_uniform_label').val('12');
                $('#padenc_uniform_label_ins').val('1200');

                $('#path_encoder_path').val('/usr/local/bin/odr-audioenc');
                $('#path_padenc_path').val('/usr/local/bin/odr-padenc');
                $('#path_sourcecompanion_path').val('/usr/local/bin/odr-sourcecompanion');
                $('#path_zmq_key_tmp_file').val('/var/tmp/zmq-'+coder_uniq_id+'.key');

                // Set value from configuration if available
                $.each( data['data'], function( section_key, section_val ) {
                    if (section_key == 'description') { $('#coder_description').html(section_val); }

                    if ( typeof section_val === 'object') {
                        $.each( section_val, function( param_key, param_val ) {
                            form_key = section_key + '_' + param_key

                            // -- To keep compatibility - can be removed ?
                            if ( form_key == 'padenc_pad_fifo_file') { form_key='padenc_pad_fifo' }
                            if ( form_key == 'padenc_dls_fifo_file') { form_key='padenc_dls_file' }
                            if ( form_key == 'source_device') { form_key='source_alsa_device' }
                            if ( form_key == 'source_url') { form_key='source_stream_url' }

                            if ( $('#'+form_key).prop('tagName') == 'INPUT' ) {
                                $('#'+form_key).val(param_val);
                            }
                            else if ( $('#'+form_key).prop('tagName') == 'SELECT' ) {
                                $('#'+form_key+' option[value="'+param_val+'"]').prop('selected', true);
                            }
                            else if ( $('#'+form_key).prop('tagName') == 'TEXTAREA' ) {
                                $('#'+form_key).text(param_val);
                            }
                            else if ( $('#'+form_key).prop('tagName') == 'DIV' ) {

                                if ( form_key == 'output_zmq_output') {
                                    $( '#'+form_key ).empty();
                                    $.each( param_val, function( param_key, param_val ) {
                                        if (param_val['enable'] == 'true') {
                                            output_zmq_enable=' checked="checked"';
                                        } else {
                                            output_zmq_enable='';
                                        }
                                        $( '#'+form_key ).append('<div class="form-group"><div class="output_zmq"><label class="control-label col-sm-2" for="output_zmq_name"></label><div class="col-sm-3"><input type="text" class="form-control" id="output_zmq_name" value="'+ param_val['name'] +'" placeholder="Description"> </div><div class="col-sm-5"><div class="input-group"><span class="input-group-addon" data-toggle="tooltip" data-placement="top" title="Check to enable the output"><input type="checkbox" id="output_zmq_enable"'+ output_zmq_enable +'></span><input type="text" class="form-control" id="output_zmq_host" value="'+ param_val['host'] +'" placeholder="Host or IP"><span class="input-group-addon">:</span><input type="text" class="form-control" id="output_zmq_port"  value="'+ param_val['port'] +'" placeholder="Port"><span class="input-group-btn"><button class="btn btn-danger btn_output_zmq_del" type="button" onclick="$(this).parent().parent().parent().parent().parent().remove()"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></span></div></div></div></div>')
                                    });
                                }

                            }
                            else {
                                debug = section_key + '_' + param_key + ':' + param_val;
                                console.log('Not found in form: '+debug);
                            }
                        });
                    }
                });
                setEnableDisable();
                if (reload == true) {
                    $.gritter.add({
                        title: 'Reload configuration',
                        image: '/fonts/accept.png',
                        text: 'Ok',
                    });
                }
            } else {
                $.gritter.add({
                    title: 'Load configuration',
                    text: "ERROR = " + data['status'] + " : " + data['statusText'],
                    image: '/fonts/warning.png',
                    sticky: true,
                });
            }
        }
    });
}

function setConfiguration() {
        var zmq_output = [];
        $('#output_zmq_output > .form-group > .output_zmq').each(function () {
            var $input = $(this)
            if ( $input.find('#output_zmq_enable').is(":checked") ) {
                    zmq_output_enable='true';
            } else {
                    zmq_output_enable='false';
            }
            zmq_output.push({name: $input.find('#output_zmq_name').val(), host: $input.find('#output_zmq_host').val(), port: $input.find('#output_zmq_port').val(), enable: zmq_output_enable});
        });

        coder_uniq_id = $('#tab_coder li.active p.coder_uniq_id').tab('show').html()

        console.log('Save configuration for: '+coder_uniq_id)

        var param = {
            "uniq_id": coder_uniq_id,
            "path" : {
                        "encoder_path": $('#path_encoder_path').val(),
                        "padenc_path": $('#path_padenc_path').val(),
                        "sourcecompanion_path": $('#path_sourcecompanion_path').val(),
                        "zmq_key_tmp_file": $('#path_zmq_key_tmp_file').val(),
                    },
            "source" : {
                        "type": $('#source_type').val(),
                        "stats_socket": $('#source_stats_socket').val(),
                        "stream_url": $('#source_stream_url').val(),
                        "stream_writeicytext": $('#source_stream_writeicytext').val(),
                        "alsa_device": $('#source_alsa_device').val(),
                        "driftcomp": $('#source_driftcomp').val(),
                        "silence_detect": $('#source_silence_detect').val(),
                        "silence_duration": $('#source_silence_duration').val(),
                        "avt_input_uri": $('#source_avt_input_uri').val(),
                        "avt_control_uri": $('#source_avt_control_uri').val(),
                        "avt_pad_port": $('#source_avt_pad_port').val(),
                        "avt_jitter_size": $('#source_avt_jitter_size').val(),
                        "avt_timeout": $('#source_avt_timeout').val(),
                        "aes67_sdp_file": $('#source_aes67_sdp_file').val(),
                        "aes67_sdp": $('#source_aes67_sdp').val(),
                    },
            "output" : {
                        "type": $('#output_type').val(),
                        "zmq_output": zmq_output,
                        "zmq_key": $('#output_zmq_key').val(),
                        "bitrate": $('#output_bitrate').val(),
                        "samplerate": $('#output_samplerate').val(),
                        "channels": $('#output_channels').val(),
                        "dabp_sbr": $('#output_dabp_sbr').val(),
                        "dabp_ps": $('#output_dabp_ps').val(),
                        "dabp_afterburner": $('#output_dabp_afterburner').val(),
                        "dab_dabmode": $('#output_dab_dabmode').val(),
                        "dab_dabpsy": $('#output_dab_dabpsy').val()
                    },
            "padenc" : {
                        "enable": $('#padenc_enable').val(),
                        "pad": $('#padenc_pad').val(),
                        "pad_fifo": $('#padenc_pad_fifo').val(),
                        "dls_file": $('#padenc_dls_file').val(),
                        "slide_directory": $('#padenc_slide_directory').val(),
                        "slide_sleeping": $('#padenc_slide_sleeping').val(),
                        "slide_once": $('#padenc_slide_once').val(),
                        "raw_dls": $('#padenc_raw_dls').val(),
                        "uniform": $('#padenc_uniform').val(),
                        "uniform_label": $('#padenc_uniform_label').val(),
                        "uniform_label_ins": $('#padenc_uniform_label_ins').val(),
                        "uniform_init_burst": $('#padenc_uniform_init_burst').val()
                    },
        }

        $.ajax({
            type: "POST",
            url: "/api/setConfig",
            data: JSON.stringify(param),
            contentType: 'application/json',
            dataType: 'text',

            error: function(data) {
                //console.log(data);
                $.gritter.add({
                    title: 'Write changes',
                    text: "ERROR = " + data['status'] + "<br />" + data['statusText'],
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
                        title: 'Write changes',
                        image: '/fonts/accept.png',
                        text: 'Ok',
                    });
                } else {
                    $.gritter.add({
                        title: 'Write changes',
                        text: "ERROR = " + data['status'] + "<br />" + data['statusText'],
                        image: '/fonts/warning.png',
                        sticky: true,
                    });
                }
            }
        });
}

function setEnableDisable(){
    if ($('#source_display').is(':checked')) {
        $('.source_type').show();
    } else {
        $('.source_type').hide();
    }

    if ($('#source_type').val() == 'stream') {
        $('#source_type_stream').show();
        $('#source_stream_url').prop('disabled', false);
        $('#source_stream_writeicytext').prop('disabled', false);
        $('#source_alsa_device').prop('disabled', true);
        $('#btn_list_alsa_devices').prop('disabled', true);
        $('#source_driftcomp').prop('disabled', false);
        $('#source_silence_detect').prop('disabled', false);
        $('#source_silence_duration').prop('disabled', false);
        $('#source_avt_input_uri').prop('disabled', true);
        $('#source_avt_control_uri').prop('disabled', true);
        $('#source_avt_pad_port').prop('disabled', true);
        $('#source_avt_jitter_size').prop('disabled', true);
        $('#source_avt_timeout').prop('disabled', true);
        $('#btn_avt_view').prop('disabled', true);
        $('#source_aes67_sdp').prop('disabled', true);
        $('#source_aes67_sdp_file').prop('disabled', true);
        $('#btn_aes67_wizard').prop('disabled', true);
        $('#output_type').prop('disabled', false);
        $('#output_zmq_host').prop('disabled', false);
        $('#output_zmq_key').prop('disabled', false);
        $('#output_bitrate').prop('disabled', false);
        $('#output_samplerate').prop('disabled', false);
        $('#output_channels').prop('disabled', false);
        if ($('#output_type').val() == 'dab') {
            $('#output_dabp_sbr').prop('disabled', true);
            $('#output_dabp_ps').prop('disabled', true);
            $('#output_dabp_afterburner').prop('disabled', true);
            $('#output_dab_dabmode').prop('disabled', false);
            $('#output_dab_dabpsy').prop('disabled', false);
            $("#output_samplerate option").filter( "[value='48000'], [value='24000']" ).prop('disabled', false);
            $("#output_samplerate option").filter( "[value='32000']" ).prop('disabled', true);
        }
        if ($('#output_type').val() == 'dabp') {
            $('#output_dabp_sbr').prop('disabled', false);
            $('#output_dabp_ps').prop('disabled', false);
            $('#output_dabp_afterburner').prop('disabled', false);
            $('#output_dab_dabmode').prop('disabled', true);
            $('#output_dab_dabpsy').prop('disabled', true);
            $("#output_samplerate option").filter( "[value='48000'], [value='32000']" ).prop('disabled', false);
            $("#output_samplerate option").filter( "[value='24000']" ).prop('disabled', true);
        }
    }

    if ($('#source_type').val() == 'alsa') {
        $('#source_type_alsa').show();
        $('#source_stream_url').prop('disabled', true);
        $('#source_stream_writeicytext').prop('disabled', true);
        $('#source_alsa_device').prop('disabled', false);
        $('#btn_list_alsa_devices').prop('disabled', false);
        $('#source_driftcomp').prop('disabled', false);
        $('#source_silence_detect').prop('disabled', false);
        $('#source_silence_duration').prop('disabled', false);
        $('#source_avt_input_uri').prop('disabled', true);
        $('#source_avt_control_uri').prop('disabled', true);
        $('#source_avt_pad_port').prop('disabled', true);
        $('#source_avt_jitter_size').prop('disabled', true);
        $('#source_avt_timeout').prop('disabled', true);
        $('#btn_avt_view').prop('disabled', true);
        $('#source_aes67_sdp').prop('disabled', true);
        $('#source_aes67_sdp_file').prop('disabled', true);
        $('#btn_aes67_wizard').prop('disabled', true);
        $('#output_type').prop('disabled', false);
        $('#output_zmq_host').prop('disabled', false);
        $('#output_zmq_key').prop('disabled', false);
        $('#output_bitrate').prop('disabled', false);
        $('#output_samplerate').prop('disabled', false);
        $('#output_channels').prop('disabled', false);
        if ($('#output_type').val() == 'dab') {
            $('#output_dabp_sbr').prop('disabled', true);
            $('#output_dabp_ps').prop('disabled', true);
            $('#output_dabp_afterburner').prop('disabled', true);
            $('#output_dab_dabmode').prop('disabled', false);
            $('#output_dab_dabpsy').prop('disabled', false);
        }
        if ($('#output_type').val() == 'dabp') {
            $('#output_dabp_sbr').prop('disabled', false);
            $('#output_dabp_ps').prop('disabled', false);
            $('#output_dabp_afterburner').prop('disabled', false);
            $('#output_dab_dabmode').prop('disabled', true);
            $('#output_dab_dabpsy').prop('disabled', true);
        }
    }

    if ($('#source_type').val() == 'avt') {
        $('#source_type_avt').show();
        $('#source_stream_url').prop('disabled', true);
        $('#source_stream_writeicytext').prop('disabled', true);
        $('#source_alsa_device').prop('disabled', true);
        $('#btn_list_alsa_devices').prop('disabled', true);
        $('#source_driftcomp').prop('disabled', true);
        $('#source_silence_detect').prop('disabled', true);
        $('#source_silence_duration').prop('disabled', true);
        $('#source_avt_input_uri').prop('disabled', false);
        $('#source_avt_control_uri').prop('disabled', false);
        $('#source_avt_pad_port').prop('disabled', false);
        $('#source_avt_jitter_size').prop('disabled', false);
        $('#source_avt_timeout').prop('disabled', false);
        $('#btn_avt_view').prop('disabled', false);
        $('#source_aes67_sdp').prop('disabled', true);
        $('#source_aes67_sdp_file').prop('disabled', true);
        $('#btn_aes67_wizard').prop('disabled', true);
        $('#output_type').prop('disabled', false);
        $('#output_zmq_host').prop('disabled', false);
        $('#output_zmq_key').prop('disabled', false);
        $('#output_bitrate').prop('disabled', false);
        $('#output_samplerate').prop('disabled', false);
        $('#output_channels').prop('disabled', false);
        if ($('#output_type').val() == 'dab') {
            $('#output_dabp_sbr').prop('disabled', true);
            $('#output_dabp_ps').prop('disabled', true);
            $('#output_dabp_afterburner').prop('disabled', true);
            $('#output_dab_dabmode').prop('disabled', false);
            $('#output_dab_dabpsy').prop('disabled', false);
        }
        if ($('#output_type').val() == 'dabp') {
            $('#output_dabp_sbr').prop('disabled', false);
            $('#output_dabp_ps').prop('disabled', false);
            $('#output_dabp_afterburner').prop('disabled', true);
            $('#output_dab_dabmode').prop('disabled', true);
            $('#output_dab_dabpsy').prop('disabled', true);
        }
    }

    if ($('#source_type').val() == 'aes67') {
        $('#source_type_aes67').show();
        $('#source_stream_url').prop('disabled', true);
        $('#source_stream_writeicytext').prop('disabled', true);
        $('#source_alsa_device').prop('disabled', true);
        $('#btn_list_alsa_devices').prop('disabled', true);
        $('#source_driftcomp').prop('disabled', false);
        $('#source_silence_detect').prop('disabled', false);
        $('#source_silence_duration').prop('disabled', false);
        $('#source_avt_input_uri').prop('disabled', true);
        $('#source_avt_control_uri').prop('disabled', true);
        $('#source_avt_pad_port').prop('disabled', true);
        $('#source_avt_jitter_size').prop('disabled', true);
        $('#source_avt_timeout').prop('disabled', true);
        $('#btn_avt_view').prop('disabled', true);
        $('#source_aes67_sdp').prop('disabled', false);
        $('#source_aes67_sdp_file').prop('disabled', false);
        $('#btn_aes67_wizard').prop('disabled', false);
        $('#output_type').prop('disabled', false);
        $('#output_zmq_host').prop('disabled', false);
        $('#output_zmq_key').prop('disabled', false);
        $('#output_bitrate').prop('disabled', false);
        $('#output_samplerate').prop('disabled', false);
        $('#output_channels').prop('disabled', false);
        if ($('#output_type').val() == 'dab') {
            $('#output_dabp_sbr').prop('disabled', true);
            $('#output_dabp_ps').prop('disabled', true);
            $('#output_dabp_afterburner').prop('disabled', true);
            $('#output_dab_dabmode').prop('disabled', false);
            $('#output_dab_dabpsy').prop('disabled', false);
        }
        if ($('#output_type').val() == 'dabp') {
            $('#output_dabp_sbr').prop('disabled', false);
            $('#output_dabp_ps').prop('disabled', false);
            $('#output_dabp_afterburner').prop('disabled', false);
            $('#output_dab_dabmode').prop('disabled', true);
            $('#output_dab_dabpsy').prop('disabled', true);
        }
    }

}

function mk_livewireplus_sdp(srcnode, chan) {
    console.log('ip: '+srcnode+', chan: '+chan)
    var b2, b3, mcastip, sdp;
    b2 = Math.floor(chan / 256);
    b3 = chan - b2 * 256;
    mcastip = "239.192." + b2 + "." + b3;

    sdp = "v=0\n";
    sdp += "o=Node 1 1 IN IP4 " + srcnode + "\n";
    sdp += "s=TestSine" + "\n";
    sdp += "t=0 0" + "\n";
    sdp += "a=type:multicast" + "\n";
    sdp += "c=IN IP4 " + mcastip + "\n";
    sdp += "m=audio 5004 RTP/AVP 97" + "\n";
    sdp += "a=rtpmap:97 L24/48000/2" + "\n";
    return sdp;
}

function updateAVTView(interval) {

    uri = $('#source_avt_control_uri').val()
    var r = /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/;
    ip = uri.match(r)[0]

    $('#btn_avt_view_refresh').prop('disabled', true);
    $("#AVTViewInfo").text("SNMP request in progress on "+ip+" ...");

    $.ajax({
        type: "GET",
        url: "/api/getAVTStatus?ip="+ip,
        contentType: 'application/json',
        dataType: 'json',

        error: function(data) {
                $.gritter.add({
                    title: 'AVT get status',
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
                $("#AVTViewInfo").text("SNMP ERROR : " + data['statusText'].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"));
            } else {
                // ADD or UPDATE ROW
                $.each( data['data'], function( key, val ) {
                    if (key == 'Encoder') {
                        console.log( data['data'][key].length )

                        $.each( data['data'][key], function( keyEM, valEM ) {
                            $.each( data['data'][key][keyEM], function( keyE, valE ) {
//                                 console.log(keyE + ':' + valE)
                                cl=''
                                if ((keyE == 'State') && (valE != 'running')) { cl='danger' }
                                if ((keyE == 'OnAir') && (valE != 'true')) { cl='danger' }
                                if ((keyE == 'AudioLevelRight') && (valE <= -40)) { cl='danger' }
                                if ((keyE == 'AudioLevelLeft') && (valE <= -40)) { cl='danger' }
                                if ((keyE == 'PadRate') && (valE == 0)) { cl='warning' }
                                tr = $('#AVTViewTableEncoder tr:contains('+keyE+')')
                                // if key already exist on table, update
                                if ( typeof tr[0] === 'undefined') {
                                    //$('#AVTViewTableEncoder > tbody:last').append('<tr class="'+cl+'"><td class="hidden">'+keyE+'</td><td>'+keyE+'</td><td>'+valE+'</td></tr>');
                                    $('#AVTViewTableEncoder > tbody:last').append('<tr><td class="hidden">'+keyE+'</td><td>'+keyE+'</td><td></td><td></td><td></td><td></td></tr>');
                                    tr = $('#AVTViewTableEncoder tr:contains('+keyE+')')
                                    tr.find('td:eq('+ (2+keyEM) +')').html(valE);
                                    tr.find('td:eq('+ (2+keyEM) +')').attr( "class", cl );
                                } else {
                                    tr.find('td:eq('+ (2+keyEM) +')').html(valE);
                                    tr.find('td:eq('+ (2+keyEM) +')').attr( "class", cl );
                                }
                            });
                        });
                    } else if (key == 'Alarms') {
                        $.each( data['data'][key], function( keyA, valA ) {
                            cl=''
                            if (valA['AlarmState'] == 'true') { cl='danger' }
                            tr = $('#AVTViewTableAlarms tr:contains('+valA['AlarmName']+')')
                            // if key already exist on table, update
                            if ( typeof tr[0] === 'undefined') {
                                $('#AVTViewTableAlarms > tbody:last').append('<tr class="'+cl+'"><td class="hidden">'+valA['AlarmName']+'</td><td>'+valA['AlarmName']+'</td><td>'+valA['AlarmState']+'</td><td>'+valA['AlarmDateTime']+'</td><td>'+valA['AlarmCount']+'</td></tr>');
                            } else {
                                tr.find('td:eq(2)').html(valA['AlarmState']);
                                tr.find('td:eq(3)').html(valA['AlarmDateTime']);
                                tr.find('td:eq(4)').html(valA['AlarmCount']);
                                tr.attr( "class", cl );
                            }
                        });
                    } else {
                        cl=''
                        if ((key == 'MainboardDsp1Workload') && (val >= 99)) { cl='danger' }
                        if ((key == 'MainboardDsp2Workload') && (val >= 99)) { cl='danger' }
                        if ((key == 'MainboardTemperature') && (val >= 60)) { cl='danger' }
                        tr = $('#AVTViewTableGlobal tr:contains('+key+')')
                        // if key already exist on table, update
                        if ( typeof tr[0] === 'undefined') {
                            $('#AVTViewTableGlobal > tbody:last').append('<tr class="'+cl+'"><td class="hidden">'+key+'</td><td>'+key+'</td><td>'+val+'</td></tr>');
                        } else {
                            tr.find('td:eq(2)').html(val);
                            tr.attr( "class", cl );
                        }
                    }
                });
                $("#AVTViewInfo").text("SNMP Ok");
            }

            $('#btn_avt_view_refresh').prop('disabled', false);
        }
    });

}

// Button handler
$(function(){
    $('#reload').click(function() {
        requestConfiguration(reload=true);
    });

    $('#save').click(function() {
        setConfiguration();
    });

    $("#source_type").change(function() {
        setEnableDisable();
    });

    $('#source_display').click(function () {
        setEnableDisable();
    });

    $("#output_type").change(function() {
        setEnableDisable();
    });

    $('#btn_list_alsa_devices').click(function () {
        $('#InfoModal h4.modal-title').text("Alsa capture devices list")
        $.ajax({
            type: "GET",
            url: "/api/getAlsaDevices",
            contentType: 'application/json',
            dataType: 'json',

            error: function(data) {
                $.gritter.add({
                    title: 'Loading alsa capture devices : ERROR !',
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
                    info = '<p>Specifying the device using parameter <b>plughw:X,Y</b>, where X=card, Y=device</p><hr />'
                    $('#InfoModal .modal-body').html(info+data['data'].replace(/\n/g,'<br />'))
                } else {
                    $.gritter.add({
                        title: 'Loading alsa capture devices',
                        text: "ERROR = " + data['status'] + " : " + data['statusText'],
                        image: '/fonts/warning.png',
                        sticky: true,
                    });
                }
            }
        });
    });

    // Modal AVT View
    $('#btn_avt_view').click(function () {
        $('#AVTViewTableGlobal tbody > tr').remove()
        $('#AVTViewTableEncoder tbody > tr').remove()
        $('#AVTViewTableAlarms tbody > tr').remove()
        updateAVTView()
    });

    $('#btn_avt_view_refresh').click(function () {
        updateAVTView()
    });


    // Modal Wizard AES67
    $('#btn_aes67_wizard').click(function () {
        $("#wizard_livewireplus_sdp").html( mk_livewireplus_sdp( $("#wizard_livewireplus_srcnodeip").val(), $("#wizard_livewireplus_channel").val() ) )
    });

    // Wizard livewireplus
    $("#wizard_livewireplus_srcnodeip").on('keyup change', function (){
        $("#wizard_livewireplus_sdp").val( mk_livewireplus_sdp( $("#wizard_livewireplus_srcnodeip").val(), $("#wizard_livewireplus_channel").val() ) )
    });
    $("#wizard_livewireplus_channel").on('keyup change', function (){
        $("#wizard_livewireplus_sdp").val( mk_livewireplus_sdp( $("#wizard_livewireplus_srcnodeip").val(), $("#wizard_livewireplus_channel").val() ) )
    });
    $('#btn_wizard_livewireplus_copy').click(function () {
        $("#source_aes67_sdp").val( $("#wizard_livewireplus_sdp").val() )
        $('#AES67WizardModal').modal('hide');
    });

    // Add ZMQ output
    $('#btn_output_zmq_add').click(function () {
        if ( $('#add_output_zmq_enable').is(":checked") ) {
            output_zmq_enable=' checked="checked"';
        } else {
            output_zmq_enable='';
        }
        $( '#output_zmq_output' ).append('<div class="form-group"><div class="output_zmq"><label class="control-label col-sm-2" for="output_zmq_name"></label><div class="col-sm-3"><input type="text" class="form-control" id="output_zmq_name" value="'+ $('#add_output_zmq_name').val().replace(/(['"])/g, "") +'" placeholder="Description"> </div><div class="col-sm-5"><div class="input-group"><span class="input-group-addon" data-toggle="tooltip" data-placement="top" title="Check to enable the output"><input type="checkbox" id="output_zmq_enable" '+ output_zmq_enable +'></span><input type="text" class="form-control" id="output_zmq_host" value="'+ $('#add_output_zmq_host').val().replace(/(['"])/g, "") +'" placeholder="Host or IP"><span class="input-group-addon">:</span><input type="text" class="form-control" id="output_zmq_port"  value="'+ $('#add_output_zmq_port').val().replace(/(['"])/g, "") +'" placeholder="Port"><span class="input-group-btn"><button class="btn btn-danger btn_output_zmq_del" type="button" onclick="$(this).parent().parent().parent().parent().parent().remove()"> <span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></span></div></div></div></div>')
        $('#add_output_zmq_name').val('');
        $('#add_output_zmq_host').val('');
        $('#add_output_zmq_port').val('');
    });
});


// ToolTip init
$(function(){
    $('[data-toggle="tooltip"]').tooltip();
});

// Onload
$(function(){
    requestCoder();
});
