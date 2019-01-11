// 
// Copyright (C) 2018 Yoann QUERET <yoann@queret.net>
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


function requestConfiguration(callback) {
    $.ajax({
        type: "GET",
        url: "/api/getConfig",
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
            if ( data['status'] == '0' ) {
                $.each( data['data'], function( section_key, section_val ) {
                    if ( typeof section_val === 'object') {
                        $.each( section_val, function( param_key, param_val ) {
                            form_key = section_key + '_' + param_key

                            // -- To keep compatibility
                            if ( form_key == 'padenc_pad_fifo_file') { form_key='padenc_pad_fifo' }
                            if ( form_key == 'padenc_dls_fifo_file') { form_key='padenc_dls_file' }

                            if ( $('#'+form_key).prop('tagName') == 'INPUT' ) {
                                $('#'+form_key).val(param_val);
                            }
                            else if ( $('#'+form_key).prop('tagName') == 'SELECT' ) {
                                $('#'+form_key+' option[value="'+param_val+'"]').prop('selected', true);
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

function setConfiguration(callback) {
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

        var param = {
         "path" : {
                     "encoder_path": $('#path_encoder_path').val(),
                     "padenc_path": $('#path_padenc_path').val(),
                     "sourcecompanion_path": $('#path_sourcecompanion_path').val(),
                     "zmq_key_tmp_file": $('#path_zmq_key_tmp_file').val(),
                 },
         "source" : {
                     "type": $('#source_type').val(),
                     "url": $('#source_url').val(),
                     "device": $('#source_device').val(),
                     "driftcomp": $('#source_driftcomp').val(),
                     "avt_input_uri": $('#source_avt_input_uri').val(),
                     "avt_control_uri": $('#source_avt_control_uri').val(),
                     "avt_pad_port": $('#source_avt_pad_port').val(),
                     "avt_jitter_size": $('#source_avt_jitter_size').val(),
                     "avt_timeout": $('#source_avt_timeout').val(),
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
                   text: "ERROR = " + data['status'] + " : " + data['statusText'],
                   image: '/fonts/warning.png',
                   sticky: true,
               });
           },
           success: function(data) {
              data = jQuery.parseJSON(data)
              if ( data['status'] == '0' ) {
                   $.gritter.add({
                       title: 'Write changes',
                       image: '/fonts/accept.png',
                       text: 'Ok',
                   });
               } else {
                   $.gritter.add({
                       title: 'Write changes',
                       text: "ERROR = " + data['status'] + " : " + data['statusText'],
                       image: '/fonts/warning.png',
                       sticky: true,
                   });
               }
           }
       });
}

function setEnableDisable(){
    if ($('#source_type').val() == 'stream') {
        $('#source_url').prop('disabled', false);
        $('#source_device').prop('disabled', true);
        $('#source_driftcomp').prop('disabled', false);
        $('#source_avt_input_uri').prop('disabled', true);
        $('#source_avt_control_uri').prop('disabled', true);
        $('#source_avt_pad_port').prop('disabled', true);
        $('#source_avt_jitter_size').prop('disabled', true);
        $('#source_avt_timeout').prop('disabled', true);
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
        $('#source_url').prop('disabled', true);
        $('#source_device').prop('disabled', false);
        $('#source_driftcomp').prop('disabled', false);
        $('#source_avt_input_uri').prop('disabled', true);
        $('#source_avt_control_uri').prop('disabled', true);
        $('#source_avt_pad_port').prop('disabled', true);
        $('#source_avt_jitter_size').prop('disabled', true);
        $('#source_avt_timeout').prop('disabled', true);
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
        $('#source_url').prop('disabled', true);
        $('#source_device').prop('disabled', true);
        $('#source_driftcomp').prop('disabled', true);
        $('#source_avt_input_uri').prop('disabled', false);
        $('#source_avt_control_uri').prop('disabled', false);
        $('#source_avt_pad_port').prop('disabled', false);
        $('#source_avt_jitter_size').prop('disabled', false);
        $('#source_avt_timeout').prop('disabled', false);
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
}

// Button handler
$(function(){
    $('#reload').click(function() {
        requestConfiguration();
        $.gritter.add({
                    title: 'Reload configuration',
                    image: '/fonts/accept.png',
                    text: 'Ok',
                });
    });

    $('#save').click(function() {
        setConfiguration();
    });

    $("#source_type").change(function() {
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
    requestConfiguration();
});
