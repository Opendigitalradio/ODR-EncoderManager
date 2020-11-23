
$(function(){
    // Hightlight menu
    page_fl = window.location.pathname.split('/')[1]
    String.prototype.inList=function(list){
        return (list.indexOf(this.toString()) != -1)
    }
    
    if (page_fl.inList(['help','about'])) {
        $( "#help_menu" ).addClass('active');
    }
    if (page_fl.inList(['backup','user', 'network'])) {
        $( "#tools_menu" ).addClass('active');
    }
    if (page_fl.inList(['encoderconfig','encodermanage'])) {
        $( "#encoder_menu" ).addClass('active');
    }
    if (page_fl.inList(['status'])) {
        $( "#status_menu" ).addClass('active');
    }
    if (page_fl.inList(['', 'home'])) {
        $( "#home_menu" ).addClass('active');
    }
    
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
                    menu_plugin = '\
                        <li id="plugins_menu" class="dropdown">\
                            <a class="dropdown-toggle" data-toggle="dropdown" href="#">Plugins\
                            <span class="caret"></span></a>\
                            <ul class="dropdown-menu" id="plugins_submenu">'
                    $.each( data['plugins'], function( key, val ) {
                        menu_plugin += '<li><a href="/plugins/'+val+'/">'+val+'</a></li>'
                    })
                    menu_plugin += '\
                            </ul>\
                        </li>\
                    '
                    $("ul#main_menu>li:last").after(menu_plugin);
                }
                if (page_fl.inList(['plugins'])) {
                    $( "#plugins_menu" ).addClass('active');
                }
                
                // Display network menu
                if (data['is_network']) {
                    $("ul#tools_submenu>li:last").after('<li><a href="/network">Networks management</a></li>')
                }
                
                
            } else {
                console.log('Error');
            }
        }
    });
    
    
    
    
});
