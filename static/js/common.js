$(function(){
    $.ajax({
        type: "POST",
        url: "/api/info",
        contentType: 'application/json',
        dataType: 'text',

        error: function(data) {
            console.log(data);
        },
        success: function(data) {
            data = jQuery.parseJSON(data)
            if (data['status'] == '-401') {
                console.log('Session timeout. Please login again.')
            } else
            if ( data['status'] == '0' ) {               
                // Display plugins menu
                if (data['plugins'].length >> 0) {
                    console.log('menu');
                    menu_plugin = '\
                        <li class="dropdown">\
                            <a class="dropdown-toggle" data-toggle="dropdown" href="#">Plugins\
                            <span class="caret"></span></a>\
                            <ul class="dropdown-menu">'
                    $.each( data['plugins'], function( key, val ) {
                        menu_plugin += '<li><a href="/plugins/'+val+'/">'+val+'</a></li>'
                    })
                    menu_plugin += '\
                            </ul>\
                        </li>\
                    '
                    $("ul#main_menu>li:last").after(menu_plugin);
                }
                
            } else {
                console.log('Error');
            }
        }
    });
});
